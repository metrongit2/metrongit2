import httpx, os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN")
org = os.getenv("GITHUB_ORG")

url = f"https://api.github.com/orgs/{org}/repos"
headers = {"Authorization": f"Bearer {token}"}

try:
    r = httpx.get(url, headers=headers, timeout=10)
    print("Status:", r.status_code)
    print("Response:", r.text[:200])
except Exception as e:
    print("Error:", e)