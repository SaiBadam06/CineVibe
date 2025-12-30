import httpx
import asyncio
import json

async def verify():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Telugu Search
        r_te = await client.post("http://127.0.0.1:8000/recommend", json={"mood": "Action Drama in Telugu"})
        telugu_top = r_te.json()["movies"][0]["title"] if r_te.json()["movies"] else "None"
        
        # Hindi Search
        r_hi = await client.post("http://127.0.0.1:8000/recommend", json={"mood": "Action Drama in Hindi"})
        hindi_top = r_hi.json()["movies"][0]["title"] if r_hi.json()["movies"] else "None"
        
        print(f"Telugu Results: {[m['title'] for m in r_te.json()['movies'][:3]]}")
        print(f"Hindi Results: {[m['title'] for m in r_hi.json()['movies'][:3]]}")
        
        if telugu_top != hindi_top:
            print("✅ SUCCESS: Results are different based on native language priority!")
        else:
            print("⚠️ WARNING: Top results are still the same. Check scoring logic.")

if __name__ == "__main__":
    asyncio.run(verify())
