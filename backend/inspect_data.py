import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

print("--- Inspecting 'Pushpa: The Rise' ---")
response = supabase.table("movies").select("*").ilike("title", "%Pushpa%").execute()
for m in response.data:
    print(f"Title: {m['title']}")
    print(f"Genre: {m['genre']}")
    print(f"Lang : {m.get('language', 'N/A')}")
    print(f"Desc : {m['description']}")
    print(f"Tags : {m['mood_tags']}")
    print("-" * 20)

print("\n--- Inspecting 'Sarkaru Vaari Paata' ---")
response = supabase.table("movies").select("*").ilike("title", "%Sarkaru%").execute()
for m in response.data:
    print(f"Title: {m['title']}")
    print(f"Desc : {m['description']}")
    print("-" * 20)
