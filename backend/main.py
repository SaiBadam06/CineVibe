from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from groq import Groq
import json

load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    mood_text = request.mood
    keywords = []
    target_genre = None

    # 1. Use Groq AI to parse mood
    if groq_client:
        try:
            prompt = f"""
            Analyze the user mood: "{mood_text}".
            Return a JSON object with:
            1. "target_genre": The single most dominant movie genre needed (e.g. Horror, Comedy, Sci-Fi, Romance). If ambiguous or mixed, use "General".
            2. "keywords": list of 3-5 specific adjective keywords.
            3. "search_term": A single best 1-2 word search phrase.
            
            Example output: {{ "target_genre": "Horror", "keywords": ["scary", "dark"], "search_term": "horror" }}
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
            print(f"AI Analysis: {data}")
            
        except Exception as e:
            print(f"Groq AI Error: {e}")
            keywords = mood_text.split()
            target_genre = "General"

    if not keywords: 
        keywords = mood_text.split()

    # 2. Check Database for Target Genre & Dynamic Seeding
    generated_new = False
    
    if target_genre and target_genre != "General":
        # Check if we have movies of this genre
        # Note: 'genre' column is text, so we check ilike
        genre_check = supabase.table("movies").select("id").ilike("genre", f"%{target_genre}%").limit(1).execute()
        
        if not genre_check.data:
            print(f"No movies found for genre '{target_genre}'. Generating on-demand...")
            try:
                # Dynamic Generation Block
                gen_prompt = f"Generate 5 high-quality, real {target_genre} movies. Fields: title, description, genre, mood_tags (list), poster_url (use placeholder https://placehold.co/600x900?text=Movie), ott (Netflix/Prime). JSON 'movies' list."
                
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
        for movie in all_movies:
            score = 0
            movie_features = set()
            if movie['genre']: movie_features.add(movie['genre'].lower())
            if movie['mood_tags']: 
                for t in movie['mood_tags']: movie_features.add(t.lower())
                
            full_text = (f"{movie['title']} {movie['description']} {movie['genre']}").lower()

            for k in keywords:
                k_lower = k.lower()
                if k_lower in movie_features:
                    score += 3
                elif k_lower in full_text:
                    score += 1
            
            # Boost score significantly if it matches the generated target genre
            # This ensures "Funny" -> "Comedy" movies rank way higher than "Action" movies with "funny" tags
            if target_genre and target_genre.lower() != "general":
                 if target_genre.lower() in (movie['genre'] or '').lower():
                     score += 10
                 # Also check slight variations or if it's the primary genre
                 elif (movie['genre'] or '').lower().startswith(target_genre.lower()):
                     score += 10

            if score > 0:
                scored_movies.append((score, movie))
        
        scored_movies.sort(key=lambda x: x[0], reverse=True)
        top_movies = [m[1] for m in scored_movies[:10]]
        
        match_type = "exact" if (scored_movies and scored_movies[0][0] >= 3) else "related"
        if not top_movies: match_type = "none"

        return {
            "movies": top_movies, 
            "keywords_used": keywords,
            "match_type": match_type,
            "generated_new": generated_new,
            "target_genre": target_genre
        }

    except Exception as e:
        print(f"Db Error: {e}")
        return {"movies": [], "error": str(e)}
