from fastapi import FastAPI
from src.services.repo_scanner import get_inactive_repositories
from src.services.user_scanner import get_inactive_collaborators

app = FastAPI(title="GitSafeOps")

@app.get("/")
def home():
    return {"message": "GitSafeOps API running"}

@app.get("/scan/repos")
async def scan_repos(days: int = 30):
    """
    Scan organization repositories for inactivity.
    """
    inactive_repos = await get_inactive_repositories(days=days)
    return {"inactive_repositories": inactive_repos}

@app.get("/scan/inactive")
async def scan_inactive_users(days: int = 30):
    """
    Scan organization collaborators for inactivity.
    """
    inactive_users = await get_inactive_collaborators(days=days)
    return {"inactive_collaborators": inactive_users}
