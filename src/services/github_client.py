import httpx
from src.utils.config import settings

GITHUB_API = "https://api.github.com"

async def get_repos():
    headers = {
        "Authorization": f"token {settings.github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"{GITHUB_API}/orgs/{settings.github_org}/repos"

    # Add timeout and better error handling
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"❌ GitHub API error: {e.response.status_code} - {e.response.text}")
            return []
        except httpx.ConnectTimeout:
            print("❌ Connection timed out while connecting to GitHub API.")
            return []
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return []
