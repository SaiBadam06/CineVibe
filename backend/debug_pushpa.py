import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

res = supabase.table("movies").select("*").ilike("title", "%Pushpa%").execute()
for m in res.data:
    print(f"TITLE: {m['title']}")
    print(f"LANGS: {m.get('languages')}")
    print(f"DESC:  {m.get('description')}")
    print(f"GENRE: {m.get('genre')}")
    print("-" * 30)
