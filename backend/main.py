from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from groq import Groq
import json
import asyncio
from watchmode_service import get_streaming_info

load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for simplicity in this demo. For prod, you might restrict this.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Clients
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
groq_api_key: str = os.environ.get("GROQ_API_KEY")

supabase: Client = None
if url and key:
    supabase = create_client(url, key)

groq_client = None
if groq_api_key:
    groq_client = Groq(api_key=groq_api_key)

class MoodRequest(BaseModel):
    mood: str


@app.get("/")
def read_root():
    return {"message": "Vibe Movie Recommender API Running (Groq Powered)"}

@app.post("/recommend")
async def recommend_movies(request: MoodRequest):
    # Sanitize input
    mood_text = "".join(c for c in request.mood if ord(c) >= 32)[:300]
    print(f"\n--- REQUEST RECEIVED: {mood_text[:50]} ---")
    
    if not supabase:
        print("Supabase not configured, raising HTTPException.")
        raise HTTPException(status_code=500, detail="Supabase not configured")

    keywords = []
    target_genre = None
    target_language = "Any" # Default to Any

    # 1. Use Groq AI to parse mood
    if groq_client:
        try:
            prompt = f"""
            Analyze the user mood: "{mood_text}".
            Return a JSON object with:
            1. "target_genre": The single most dominant movie genre needed (e.g. Horror, Comedy, Sci-Fi, Romance). If ambiguous or mixed, use "General".
            2. "keywords": list of 3-5 specific adjective keywords.
            3. "search_term": A single best 1-2 word search phrase.
            4. "target_language": The requested language (e.g. "English", "Hindi", "Telugu", "Korean", "Any"). Default to "Any" if not specified.
            
            Example output: {{ "target_genre": "Horror", "keywords": ["scary", "dark"], "search_term": "horror", "target_language": "English" }}
            """
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a movie expert. Return strictly JSON."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}, 
            )
            
            content = chat_completion.choices[0].message.content
            data = json.loads(content)
            keywords = data.get("keywords", [])
            target_genre = data.get("target_genre", "General")
            target_language = data.get("target_language", "Any")
            print(f"AI Analysis: {data}")
            
        except Exception as e:
            print(f"Groq AI Error: {e}")
            keywords = mood_text.split()
            target_genre = "General"
            target_language = "Any"

    if not keywords: 
        keywords = mood_text.split()

    # 2. Check Database for Target Genre & Dynamic Seeding
    generated_new = False
    
    if target_genre and target_genre != "General":
        # Check if we have movies of this genre
        # Note: 'genre' column is text, so we check ilike
        genre_check = supabase.table("movies").select("id").ilike("genre", f"%{target_genre}%").limit(1).execute()
        
        # If we need to generate, include language in prompt
        if not genre_check.data:
            print(f"No movies found for genre '{target_genre}'. Generating on-demand...")
            try:
                # Dynamic Generation Block
                lang_instruction = f"in {target_language} language" if target_language != "Any" else ""
                gen_prompt = f"Generate 5 high-quality, real {target_genre} movies {lang_instruction} that match these specific vibes/keywords: {', '.join(keywords)}. Fields: title, description, genre, languages (list of all languages the movie is released in), mood_tags (list), poster_url (use placeholder https://placehold.co/600x900?text=Movie), ott (Netflix/Prime). JSON 'movies' list."
                
                gen_completion = groq_client.chat.completions.create(
                     messages=[{"role": "user", "content": gen_prompt}],
                     model="llama-3.3-70b-versatile",
                     response_format={"type": "json_object"}
                )
                gen_content = gen_completion.choices[0].message.content
                new_movies_data = json.loads(gen_content).get("movies", [])
                
                if new_movies_data:
                    # Enforce genre
                    for m in new_movies_data:
                        m["genre"] = target_genre
                        if "ott" not in m: m["ott"] = "Netflix" # fallback
                    
                    supabase.table("movies").insert(new_movies_data).execute()
                    generated_new = True
                    print(f"Seeded {len(new_movies_data)} new {target_genre} movies.")
            except Exception as e:
                print(f"Dynamic seeding failed: {e}")

    # 3. Query Supabase
    try:
        response = supabase.table("movies").select("*").execute()
        all_movies = response.data
        
        scored_movies = []
        non_english_triggers = ["bollywood", "tollywood", "hindi", "telugu", "tamil", "kannada", "malayalam", "korean", "japanese", "spanish", "french"]

        for movie in all_movies:
            score = 0
            movie_features = set()
            if movie['genre']: movie_features.add(movie['genre'].lower())
            if movie['mood_tags']: 
                for t in movie['mood_tags']: movie_features.add(t.lower())
                
            full_text = (f"{movie['title']} {movie['description'] or ''} {movie['genre'] or ''}").lower()

            for k in keywords:
                k_lower = k.lower()
                if k_lower in movie_features:
                    score += 5 # Increased from 3 to 5 to value "vibe" more
                elif k_lower in full_text:
                    score += 1
            
            # Boost score if it matches the generated target genre
            if target_genre and target_genre.lower() != "general":
                 if target_genre.lower() in (movie['genre'] or '').lower():
                     score += 4 # Reduced from 10 to 4 to prevent genre from overpowering the vibe
                 elif (movie['genre'] or '').lower().startswith(target_genre.lower()):
                     score += 4

            # --- LANGUAGE LOGIC (STRICT) ---
            movie_langs = movie.get('languages') or []
            if isinstance(movie_langs, str): movie_langs = [movie_langs] # Fallback
            movie_langs = [l.lower() for l in movie_langs]
            
            if target_language and target_language.lower() != "any":
                req_lang = target_language.lower()
                
                # Case 1: English Requested
                if req_lang == "english":
                    # If it has English in its list of languages, it's good
                    if "english" in movie_langs:
                        score += 5
                    # If it has NO English but has other languages, it's a mismatch
                    elif len(movie_langs) > 0:
                        score = -100
                    # Safety loop for description triggers
                    elif any(t in full_text for t in non_english_triggers):
                        score = -100
                
                # Case 2: Specific Foreign Language Requested (e.g., Telugu)
                elif req_lang in movie_langs:
                    # NATIVE BOOST: If it's the original language, give massive priority
                    movie_orig = (movie.get('original_language') or '').lower()
                    if req_lang == movie_orig:
                        score += 50
                    else:
                        score += 5
                
                # Case 3: Foreign requested, but movie doesn't support it
                elif req_lang in non_english_triggers:
                    if len(movie_langs) > 0 and req_lang not in movie_langs:
                        score = -100 # Strict separation

            if score > 0:
                scored_movies.append((score, movie))
        
        # Sort by score descending
        scored_movies.sort(key=lambda x: x[0], reverse=True)
        
        # Dedup and Limit
        seen_titles = set()
        top_movies = []
        for score, movie in scored_movies:
            if movie['title'] not in seen_titles:
                top_movies.append(movie)
                seen_titles.add(movie['title'])
            if len(top_movies) >= 10: break
        
        # FINAL SAFETY NET
        if not top_movies and not generated_new:
             try:
                lang_instr = f"in {target_language} language" if target_language != "Any" else ""
                gen_prompt = f"Return a JSON object with a 'movies' list containing 5 real {target_genre} movies {lang_instr} matching vibes: {', '.join(keywords)}. Each movie must have keys: title, description, genre, original_language (native), languages (list), mood_tags (list), poster_url, ott."
                gen_completion = groq_client.chat.completions.create(
                     messages=[{"role": "user", "content": gen_prompt}],
                     model="llama-3.1-8b-instant",
                     response_format={"type": "json_object"}
                )
                new_data = json.loads(gen_completion.choices[0].message.content).get("movies", [])
                if new_data:
                    for m in new_data: 
                        m["genre"] = target_genre
                        if target_language != "Any":
                             m["languages"] = [target_language]
                        if "ott" not in m: m["ott"] = "Netflix"
                    
                    supabase.table("movies").insert(new_data).execute()
                    top_movies = new_data
                    generated_new = True
             except Exception:
                pass

        # --- WATCHMODE ENRICHMENT ---
        final_movies = top_movies[:6]
        async def enrich_movie(movie):
            real_ott = await get_streaming_info(movie['title'])
            if real_ott:
                movie['ott'] = real_ott
        
        await asyncio.gather(*[enrich_movie(m) for m in final_movies])

        return {
            "movies": final_movies,
            "generated_new": generated_new,
            "target_genre": target_genre,
            "target_language": target_language,
            "match_type": "exact" if top_movies else "none"
        }

    except Exception as e:
        print(f"Db Error: {e}")
        return {"movies": [], "error": str(e)}
