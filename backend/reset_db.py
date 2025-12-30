import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Missing env vars")
    exit(1)

supabase = create_client(url, key)

print("⚠️ DELETING ALL MOVIES...")
# Delete all rows
try:
    # Reliable way to delete all rows in Supabase/PostgREST
    supabase.table("movies").delete().neq("title", "___NON_EXISTENT___").execute()
    print("✅ Database cleared.")
except Exception as e:
    print(f"Error clearing DB: {e}")

print("🌱 Re-seeding...")
import seed
