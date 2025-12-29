import os
from dotenv import load_dotenv
from supabase import create_client
import time
import random

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Please set SUPABASE_URL and SUPABASE_KEY in .env")
    exit(1)

supabase = create_client(url, key)

# Base list covering various vibes/moods including international
movies_db = [
  # --- Indian / Bollywood / Regional ---
  {"title": "3 Idiots", "genre": "Comedy", "mood_tags": ["inspiring", "funny", "friendship", "emotional"], "poster_url": "https://image.tmdb.org/t/p/w500/66A9MqXOyVFCssoloscw79z8Tew.jpg"},
  {"title": "RRR", "genre": "Action", "mood_tags": ["epic", "energetic", "patriotic", "bromance"], "poster_url": "https://image.tmdb.org/t/p/w500/nEufeZlyAOLqO2brrs0yeF1lgXO.jpg"},
  {"title": "Dangal", "genre": "Drama", "mood_tags": ["inspiring", "sports", "family", "intense"], "poster_url": "https://image.tmdb.org/t/p/w500/mY7SeH4HFFxW1hiIGV3FpNR2G7h.jpg"},
  {"title": "Lagaan", "genre": "Drama", "mood_tags": ["hopeful", "sports", "historic", "long"], "poster_url": "https://image.tmdb.org/t/p/w500/uCAk4Yh4u4n3eL3PZ6o5z7eqq.jpg"},
  {"title": "Dilwale Dulhania Le Jayenge", "genre": "Romance", "mood_tags": ["classic", "feel-good", "romantic", "musical"], "poster_url": "https://image.tmdb.org/t/p/w500/2cal2433yVSpNrCmBjS41cU.jpg"},
  {"title": "Kantara", "genre": "Thriller", "mood_tags": ["mystical", "intense", "folklore", "action"], "poster_url": "https://image.tmdb.org/t/p/w500/p58.jpg"}, # Placeholder link
  
  # --- Korean ---
  {"title": "Oldboy", "genre": "Thriller", "mood_tags": ["dark", "revenge", "shocking", "violent"], "poster_url": "https://image.tmdb.org/t/p/w500/pWDtjs568ZfOTMbURQBYuT4Qxka.jpg"},
  {"title": "Train to Busan", "genre": "Horror", "mood_tags": ["intense", "zombies", "emotional", "action"], "poster_url": "https://image.tmdb.org/t/p/w500/34rwboSDCg6n2a1eZl6.jpg"},
  {"title": "The Handmaiden", "genre": "Drama", "mood_tags": ["erotic", "twist", "beautiful", "suspense"], "poster_url": "https://image.tmdb.org/t/p/w500/8j4.jpg"}, # Partial link

  # --- Anime ---
  {"title": "Your Name", "genre": "Animation", "mood_tags": ["beautiful", "romantic", "supernatural", "emotional"], "poster_url": "https://image.tmdb.org/t/p/w500/q719jXXEzOoYaps6babgKnONONX.jpg"},
  {"title": "Akira", "genre": "Animation", "mood_tags": ["cyberpunk", "intense", "classic", "violent"], "poster_url": "https://image.tmdb.org/t/p/w500/ne.jpg"},

  # --- European ---
  {"title": "Amélie", "genre": "Comedy", "mood_tags": ["whimsical", "french", "feel-good", "quirky"], "poster_url": "https://image.tmdb.org/t/p/w500/sl.jpg"}, 
  {"title": "Pan's Labyrinth", "genre": "Fantasy", "mood_tags": ["dark", "fairy-tale", "sad", "spanish"], "poster_url": "https://image.tmdb.org/t/p/w500/o.jpg"},
  {"title": "The Hunt", "genre": "Drama", "mood_tags": ["unjust", "intense", "danish", "serious"], "poster_url": "https://image.tmdb.org/t/p/w500/w.jpg", "ott": "Prime Video"},

  # --- Tollywood (Telugu) ---
  {"title": "Baahubali: The Beginning", "genre": "Action", "mood_tags": ["epic", "war", "grand", "fantasy"], "poster_url": "https://image.tmdb.org/t/p/w500/9BAjt8nSSms62uOV8XbcxjGW2M3.jpg", "ott": "Netflix"},
  {"title": "Mahanati", "genre": "Biography", "mood_tags": ["emotional", "inspiring", "classic", "sad"], "poster_url": "https://image.tmdb.org/t/p/w500/p.jpg", "ott": "Prime Video"},
  {"title": "Eega", "genre": "Fantasy", "mood_tags": ["revenge", "funny", "inventive", "unique"], "poster_url": "https://image.tmdb.org/t/p/w500/u.jpg", "ott": "Netflix"},
  {"title": "Jersey", "genre": "Drama", "mood_tags": ["inspiring", "sad", "sports", "emotional"], "poster_url": "https://image.tmdb.org/t/p/w500/j.jpg", "ott": "Disney+ Hotstar"},
  {"title": "Arjun Reddy", "genre": "Romance", "mood_tags": ["intense", "dark", "passionate", "aggressive"], "poster_url": "https://image.tmdb.org/t/p/w500/a.jpg", "ott": "Prime Video"},
]

# AI Generation to fill the rest up to 150
import json
try:
    from groq import Groq
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if groq_api_key:
        print("Groq Key found! Generating international & diverse movies...")
        client = Groq(api_key=groq_api_key)
        
        # 10 iterations of 10 movies = 100 new movies
        vibes = [
            "Tollywood Action", "Tollywood Comedy", "Tollywood Mass Masala",
            "French New Wave", "Italian Neorealism", "Hong Kong Action", 
            "Bollywood Masala", "Japanese Horror", "Scandi Noir",
            "90s Indie", "Classic Western", "Cyberpunk Sci-Fi"
        ]
        
        for vibe in vibes:
            try:
                print(f"Fetching: {vibe}...")
                prompt = f"Generate a JSON list of 8 real {vibe} movies. Fields: title, genre, mood_tags (list of 3 words), description, ott (e.g. Netflix, Prime, etc - guess based on popularity). Ensure they are famous real movies."
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                content = completion.choices[0].message.content
                data = json.loads(content)
                new_movies = data.get("movies", [])
                if isinstance(data, list): new_movies = data 
                
                print(f"Generated {len(new_movies)} for vibe '{vibe}'")
                for m in new_movies:
                    # Enrich with placeholder if missing
                    if "poster_url" not in m:
                        # Use a service that generates text images or just random placeholder
                        m["poster_url"] = f"https://placehold.co/600x900/1e293b/ffffff?text={m['title'].replace(' ', '+')}"
                    movies_db.append(m)
                
                time.sleep(1) 
            except Exception as e:
                print(f"Generative error for {vibe}: {e}")
except ImportError:
    print("Groq library not found or error, skipping AI generation.")
except Exception as e:
    print(f"Skipping AI generation due to configuration: {e}")

print(f"Total movies to process: {len(movies_db)}")

for movie in movies_db:
    try:
        # Check if exists
        existing = supabase.table("movies").select("id").eq("title", movie["title"]).execute()
        if not existing.data:
            supabase.table("movies").insert(movie).execute()
            print(f"Inserted: {movie['title']}")
        else:
            print(f"Skipped (Duplicate): {movie['title']}")
    except Exception as e:
        print(f"Error processing {movie.get('title')}: {e}")

print("Seeding complete!")
