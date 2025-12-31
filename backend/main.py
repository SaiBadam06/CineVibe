from fastapi import FastAPI, HTTPException, Body, Depends, Header, Request
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

async def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = authorization.split(" ")[1]
    try:
        # Use the supabase client to verify the user
        res = supabase.auth.get_user(token)
        if not res or not res.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return res.user
    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


@app.get("/")
def read_root():
    return {"message": "Vibe Movie Recommender API Running (Groq Powered)"}

@app.get("/database-info")
async def database_info(user: any = Depends(verify_token)):
    """Get information about available movies in the database"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
    try:
        response = supabase.table("movies").select("*").execute()
        all_movies = response.data
        
        genres = {}
        languages = set()
        
        for movie in all_movies:
            # Count by genre
            genre = movie.get('genre', 'Unknown')
            genres[genre] = genres.get(genre, 0) + 1
            
            # Collect languages
            movie_langs = movie.get('languages', [])
            if isinstance(movie_langs, list):
                for lang in movie_langs:
                    languages.add(lang)
        
        return {
            "total_movies": len(all_movies),
            "genres": genres,
            "languages": sorted(list(languages)),
            "sample_movies": [m['title'] for m in all_movies[:10]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommend")
async def recommend_movies(request: MoodRequest, user: any = Depends(verify_token)):
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

    # 2. Query Database (No AI Generation)
    generated_new = False

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
            title_lower = movie['title'].lower()

            # Improved Scoring Logic
            for k in keywords:
                k_lower = k.lower()
                # Mood tag match (highest priority for vibe)
                if k_lower in movie_features:
                    score += 7
                # Title match (important for specific movie requests)
                elif k_lower in title_lower:
                    score += 5
                # Description match (contextual relevance)
                elif k_lower in full_text:
                    score += 2
            
            # Genre match (strong signal)
            if target_genre and target_genre.lower() != "general":
                 if target_genre.lower() in (movie['genre'] or '').lower():
                     score += 10
                 elif (movie['genre'] or '').lower().startswith(target_genre.lower()):
                     score += 8

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
        
        # Better Fallback - show available database content
        available_genres = set()
        available_languages = set()
        for m in all_movies:
            if m.get('genre'): available_genres.add(m['genre'])
            if m.get('languages'):
                for lang in m['languages']:
                    available_languages.add(lang)
        
        # If no matches, return message with database info
        if not top_movies:
            print(f"No strong matches found. Available genres: {available_genres}")
            # Return best-scored movies even if score is low
            if scored_movies:
                top_movies = [movie for _, movie in scored_movies[:6]]

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
            "match_type": "exact" if top_movies else "none",
            "available_genres": list(available_genres),
            "available_languages": list(available_languages),
            "total_in_db": len(all_movies)
        }

    except Exception as e:
        print(f"Db Error: {e}")
        return {"movies": [], "error": str(e)}
