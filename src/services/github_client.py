import httpx
import asyncio
from typing import List, Dict, Any, Optional
from src.utils.config import settings
from src.utils.logger import logger

GITHUB_API = "https://api.github.com"
DEFAULT_TIMEOUT = httpx.Timeout(20.0, connect=5.0)
HEADERS = {"Accept": "application/vnd.github.v3+json"}

def auth_headers():
    return {**HEADERS, "Authorization": f"token {settings.github_token}"}

async def _get(url: str, params: dict | None = None) -> Any:
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        r = await client.get(url, headers=auth_headers(), params=params)
        r.raise_for_status()
        return r.json()

async def list_org_repos(per_page: int = 100) -> List[Dict]:
    """List all repos for org (handles simple pagination)."""
    url = f"{GITHUB_API}/orgs/{settings.github_org}/repos"
    repos = []
    page = 1
    while True:
        params = {"per_page": per_page, "page": page, "type": "all"}
        try:
            chunk = await _get(url, params=params)
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed listing repos: {e}")
            return repos
        if not chunk:
            break
        repos.extend(chunk)
        if len(chunk) < per_page:
            break
        page += 1
        await asyncio.sleep(0.05)
    return repos

async def get_repo(owner: str, repo: str) -> Dict:
    url = f"{GITHUB_API}/repos/{owner}/{repo}"
    return await _get(url)

async def list_collaborators(owner: str, repo: str) -> List[Dict]:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/collaborators"
    return await _get(url)

async def list_pull_requests(owner: str, repo: str, state: str = "open") -> List[Dict]:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls"
    return await _get(url, params={"state": state, "per_page": 100})

async def get_commit_history(owner: str, repo: str, author: Optional[str] = None, per_page: int = 30) -> List[Dict]:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits"
    params = {"per_page": per_page}
    if author:
        params["author"] = author
    return await _get(url, params=params)

async def get_file_contents(owner: str, repo: str, path: str) -> Dict:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
    return await _get(url)

async def remove_collaborator(owner: str, repo: str, username: str) -> bool:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/collaborators/{username}"
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        r = await client.delete(url, headers=auth_headers())
        logger.info(f"Remove collaborator {username} on {owner}/{repo} => {r.status_code}")
        return r.status_code in (204, 200)
