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
  {"title": "3 Idiots", "genre": "Comedy", "languages": ["Hindi"], "mood_tags": ["inspiring", "funny", "friendship", "emotional"], "poster_url": "https://image.tmdb.org/t/p/w500/66A9MqXOyVFCssoloscw79z8Tew.jpg", "description": "Two friends start a quest for a lost buddy, revisiting their college days in this Bollywood comedy."},
  {"title": "RRR", "genre": "Action", "languages": ["Telugu", "Hindi", "Tamil", "Kannada", "Malayalam"], "mood_tags": ["epic", "energetic", "patriotic", "bromance"], "poster_url": "https://image.tmdb.org/t/p/w500/nEufeZlyAOLqO2brrs0yeF1lgXO.jpg", "description": "A fearless revolutionary and an officer in the British force decide to join forces in this Tollywood epic."},
  {"title": "Dangal", "genre": "Drama", "languages": ["Hindi", "Tamil", "Telugu"], "mood_tags": ["inspiring", "sports", "family", "intense"], "poster_url": "https://image.tmdb.org/t/p/w500/mY7SeH4HFFxW1hiIGV3FpNR2G7h.jpg", "description": "Former wrestler Mahavir Singh Phogat and his two wrestler daughters struggle towards glory in Bollywood."},
  {"title": "Lagaan", "genre": "Drama", "languages": ["Hindi", "English"], "mood_tags": ["hopeful", "sports", "historic", "long"], "poster_url": "https://image.tmdb.org/t/p/w500/uCAk4Yh4u4n3eL3PZ6o5z7eqq.jpg", "description": "The people of a small village in Victorian India stake their future on a game of cricket."},
  {"title": "Dilwale Dulhania Le Jayenge", "genre": "Romance", "languages": ["Hindi"], "mood_tags": ["classic", "feel-good", "romantic", "musical"], "poster_url": "https://image.tmdb.org/t/p/w500/2cal2433yVSpNrCmBjS41cU.jpg", "description": "A young man and woman fall in love on a trip to Europe, but her father has promised her hand to another."},
  {"title": "Kantara", "genre": "Thriller", "languages": ["Kannada", "Telugu", "Hindi", "Tamil", "Malayalam"], "mood_tags": ["mystical", "intense", "folklore", "action"], "poster_url": "https://image.tmdb.org/t/p/w500/p58.jpg", "description": "A fiery young man clashes with an unflinching forest officer in a south Indian village."}, 
  
  # --- Korean ---
  {"title": "Oldboy", "genre": "Thriller", "languages": ["Korean"], "mood_tags": ["dark", "revenge", "shocking", "violent"], "poster_url": "https://image.tmdb.org/t/p/w500/pWDtjs568ZfOTMbURQBYuT4Qxka.jpg", "description": "After being kidnapped and imprisoned for fifteen years, Oh Dae-Su is released, only to find that he must find his captor in 5 days."},
  {"title": "Train to Busan", "genre": "Horror", "languages": ["Korean"], "mood_tags": ["intense", "zombies", "emotional", "action"], "poster_url": "https://image.tmdb.org/t/p/w500/34rwboSDCg6n2a1eZl6.jpg", "description": "While a zombie virus breaks out in South Korea, passengers struggle to survive on the train from Seoul to Busan."},
  {"title": "The Handmaiden", "genre": "Drama", "languages": ["Korean"], "mood_tags": ["erotic", "twist", "beautiful", "suspense"], "poster_url": "https://image.tmdb.org/t/p/w500/8j4.jpg", "description": "A woman is hired as a handmaiden to a Japanese heiress, but secretly she is involved in a plot to defraud her."},

  # --- Anime (Japanese) ---
  {"title": "Your Name", "genre": "Animation", "languages": ["Japanese", "English"], "mood_tags": ["beautiful", "romantic", "supernatural", "emotional"], "poster_url": "https://image.tmdb.org/t/p/w500/q719jXXEzOoYaps6babgKnONONX.jpg", "description": "Two strangers find themselves linked in a bizarre way. When a connection forms, will distance be the only thing to keep them apart?"},
  {"title": "Akira", "genre": "Animation", "languages": ["Japanese", "English"], "mood_tags": ["cyberpunk", "intense", "classic", "violent"], "poster_url": "https://image.tmdb.org/t/p/w500/ne.jpg", "description": "A secret military project endangers Neo-Tokyo when it turns a biker gang member into a rampaging psychic psychopath."},

  # --- European ---
  {"title": "Amélie", "genre": "Comedy", "languages": ["French"], "mood_tags": ["whimsical", "french", "feel-good", "quirky"], "poster_url": "https://image.tmdb.org/t/p/w500/sl.jpg", "description": "Amélie is an innocent and naive girl in Paris with her own sense of justice. She decides to help those around her."}, 
  {"title": "Pan's Labyrinth", "genre": "Fantasy", "languages": ["Spanish"], "mood_tags": ["dark", "fairy-tale", "sad", "spanish"], "poster_url": "https://image.tmdb.org/t/p/w500/o.jpg", "description": "In the Falangist Spain of 1944, the bookish young stepdaughter of a sadistic army officer escapes into an eerie but captivating fantasy world."},
  {"title": "The Hunt", "genre": "Drama", "languages": ["Danish"], "mood_tags": ["unjust", "intense", "danish", "serious"], "poster_url": "https://image.tmdb.org/t/p/w500/w.jpg", "ott": "Prime Video", "description": "A teacher lives a lonely life, all the while struggling over his son's custody. His life slowly gets better as he finds love and receives good news from his son."},

  # --- Tollywood (Telugu) ---
  {"title": "Baahubali: The Beginning", "genre": "Action", "languages": ["Telugu", "Hindi", "Tamil", "Malayalam"], "mood_tags": ["epic", "war", "grand", "fantasy"], "poster_url": "https://image.tmdb.org/t/p/w500/9BAjt8nSSms62uOV8XbcxjGW2M3.jpg", "ott": "Netflix", "description": "In the kingdom of Mahishmati, a fair but fierce warrior rises to save the land in this Tollywood masterpiece."},
  {"title": "Mahanati", "genre": "Biography", "languages": ["Telugu", "Tamil", "Malayalam"], "mood_tags": ["emotional", "inspiring", "classic", "sad"], "poster_url": "https://image.tmdb.org/t/p/w500/p.jpg", "ott": "Prime Video", "description": "The life of South Indian actress Savitri, who took the film industry by storm in the late 50s and 60s."},
  {"title": "Eega", "genre": "Fantasy", "languages": ["Telugu", "Hindi", "Tamil", "Malayalam"], "mood_tags": ["revenge", "funny", "inventive", "unique"], "poster_url": "https://image.tmdb.org/t/p/w500/u.jpg", "ott": "Netflix", "description": "A murdered man is reincarnated as a housefly and seeks to avenge his death in this inventive Tollywood film."},
  {"title": "Jersey", "genre": "Drama", "languages": ["Telugu", "Hindi"], "mood_tags": ["inspiring", "sad", "sports", "emotional"], "poster_url": "https://image.tmdb.org/t/p/w500/j.jpg", "ott": "Disney+ Hotstar", "description": "A failed cricketer decides to return to cricket in his late thirties driven by the desire to represent the Indian cricket team and fulfill his son's wish."},
  {"title": "Arjun Reddy", "genre": "Romance", "languages": ["Telugu"], "mood_tags": ["intense", "dark", "passionate", "aggressive"], "poster_url": "https://image.tmdb.org/t/p/w500/a.jpg", "ott": "Prime Video", "description": "Arjun Reddy Deshmukh is a high-functioning alcoholic surgeon who has anger management problems."},
  {"title": "Pushpa: The Rise", "genre": "Action", "languages": ["Telugu", "Hindi", "Tamil", "Malayalam", "Kannada"], "mood_tags": ["Intense", "Emotional", "Gritty"], "poster_url": "https://image.tmdb.org/t/p/w500/7p2rXof30NLYuclU8788fU3S8mU.jpg", "description": "A laborer rises through the ranks of a red sandal smuggling syndicate, unfolding a story of power, survival, and personal loss."},
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
                prompt = f"Generate a JSON list of 8 real {vibe} movies. Fields: title, genre, languages (list of all languages the movie is released in, e.g. ['Telugu', 'Hindi', 'Tamil']), mood_tags (list of 3 words), description, ott (e.g. Netflix, Prime, etc - guess based on popularity)."
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
                    # Enrich languages if missing and pluralize if it came as string
                    if "language" in m and "languages" not in m:
                        m["languages"] = [m["language"]]
                    elif "languages" not in m:
                        m["languages"] = []

                    # FORCE LANGUAGES FROM VIBE (Robustness Fix)
                    if "Tollywood" in vibe: 
                        for l in ["Telugu", "Hindi", "Tamil", "Malayalam"]:
                            if l not in m["languages"]: m["languages"].append(l)
                    elif "Bollywood" in vibe: 
                        for l in ["Hindi", "English"]:
                            if l not in m["languages"]: m["languages"].append(l)
                    elif "French" in vibe: 
                        if "French" not in m["languages"]: m["languages"].append("French")
                    elif "Italian" in vibe: 
                        if "Italian" not in m["languages"]: m["languages"].append("Italian")
                    elif "Japanese" in vibe: 
                        if "Japanese" not in m["languages"]: m["languages"].append("Japanese")
                    elif "Korean" in vibe: 
                        if "Korean" not in m["languages"]: m["languages"].append("Korean")
                    elif "Hong Kong" in vibe: 
                        for l in ["Cantonese", "Mandarin", "English"]:
                            if l not in m["languages"]: m["languages"].append(l)
                    elif "Scandi" in vibe: 
                        if "Swedish/Danish" not in m["languages"]: m["languages"].append("Swedish/Danish")
                    elif "Spanish" in vibe: 
                        if "Spanish" not in m["languages"]: m["languages"].append("Spanish")
                    elif "Western" in vibe or "Indie" in vibe: 
                        if "English" not in m["languages"]: m["languages"].append("English")
                    
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
