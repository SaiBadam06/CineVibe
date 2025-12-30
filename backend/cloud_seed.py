import os
from dotenv import load_dotenv
from supabase import create_client
import json

# This script helps you seed your CLOUD database from your local machine.
# Usage: python cloud_seed.py <CLOUD_URL> <CLOUD_KEY>

def seed_cloud(url, key):
    print(f"🚀 Connecting to Cloud Supabase: {url}")
    supabase = create_client(url, key)
    
    # Load movies from seed.py or a json
    from seed import movies_db
    
    print(f"🌱 Seeding {len(movies_db)} movies...")
    try:
        # MIGRATION: Ensure original_language exists
        print("🛠️ Checking cloud schema...")
        try:
            # Attempt to select the column to test existence
            supabase.table("movies").select("original_language").limit(1).execute()
        except Exception:
            print("⚠️ 'original_language' column missing. Attempting migration...")
            # We use the REST API to run SQL via RPC if enabled, or just warn the user.
            # Most Supabase proyectos don't have exec_sql enabled by default for anonymity.
            # So we will try a different approach or warn.
            print("FATAL: The cloud database is missing the 'original_language' column.")
            print("Please run this in your Supabase SQL Editor first:")
            print("ALTER TABLE movies ADD COLUMN IF NOT EXISTS original_language text;")
            return

        # Clear existing
        supabase.table("movies").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print("✅ Cloud database cleared.")
        
        # Insert new
        res = supabase.table("movies").insert(movies_db).execute()
        print(f"✅ Successfully seeded {len(res.data)} movies to Cloud!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    load_dotenv()
    
    url = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SUPABASE_URL")
    key = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("Usage: python cloud_seed.py <URL> <KEY>")
        print("Or set SUPABASE_URL and SUPABASE_KEY in .env")
    else:
        seed_cloud(url, key)
