import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# Simulation of what Main.py does
def test_scoring(mood_text, target_genre="Action", target_language="English", keywords=["action", "drama"]):
    print(f"\n--- Testing Query: '{mood_text}' (Lang: {target_language}) ---")
    
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

        # Keyword match
        for k in keywords:
            if k.lower() in movie_features:
                score += 5
            elif k.lower() in full_text:
                score += 1
        
        # Genre match
        if target_genre and target_genre.lower() != "general":
             if target_genre.lower() in (movie['genre'] or '').lower():
                 score += 4
             elif (movie['genre'] or '').lower().startswith(target_genre.lower()):
                 score += 4

        # Language Penalty Logic
        is_penalized = False
        if target_language == "English":
            if any(trigger in full_text for trigger in non_english_triggers):
                score -= 10
                is_penalized = True
        
        if score > 0 or "Pushpa" in movie['title']: # Show Pushpa even if score is low to verify penalty
            scored_movies.append((score, movie['title'], is_penalized, full_text[:50]+"..."))

    scored_movies.sort(key=lambda x: x[0], reverse=True)
    
    print(f"{'SCORE':<6} | {'TITLE':<30} | {'PENALIZED':<10} | {'TEXT START'}")
    print("-" * 80)
    for s, t, p, txt in scored_movies[:15]:
        print(f"{s:<6} | {t:<30} | {str(p):<10} | {txt}")

test_scoring("Action drama in english")
