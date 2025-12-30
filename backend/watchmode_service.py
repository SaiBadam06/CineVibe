import os
import httpx
from dotenv import load_dotenv

load_dotenv()

WATCHMODE_API_KEY = os.environ.get("WATCHMODE_API_KEY")

async def get_streaming_info(title):
    """
    Finds streaming availability for a movie title.
    Returns a string like 'Netflix, Prime Video' or None.
    """
    if not WATCHMODE_API_KEY:
        return None

    try:
        async with httpx.AsyncClient() as client:
            # 1. Search for titles
            search_url = f"https://api.watchmode.com/v1/search/?apiKey={WATCHMODE_API_KEY}&search_field=name&search_value={title}&types=movie"
            search_res = await client.get(search_url)
            search_data = search_res.json()

            if not search_data.get("title_results"):
                return None

            # Get first result ID
            title_id = search_data["title_results"][0]["id"]

            # 2. Get sources
            sources_url = f"https://api.watchmode.com/v1/title/{title_id}/sources/?apiKey={WATCHMODE_API_KEY}"
            sources_res = await client.get(sources_url)
            sources_data = sources_res.json()

            if not sources_data:
                return None

            # Extract unique source names
            names = list(set([s["name"] for s in sources_data if s["type"] == "sub"]))
            if not names:
                return "Not Streaming"
            
            return ", ".join(names[:3]) # Return top 3
    except Exception as e:
        print(f"Watchmode Error for {title}: {e}")
        return None
