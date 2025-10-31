from fastapi import FastAPI
from src.services.github_client import get_repos
from src.services.repo_scanner import analyze_repo
from src.services.user_scanner import get_inactive_collaborators

app = FastAPI(title="GitSafeOps")

@app.get("/")
def home():
    return {"message": "GitSafeOps API running"}

@app.get("/scan")
async def scan_org():
    """Scan all repos for misconfigurations."""
    repos = await get_repos()
    findings = []

    for repo in repos:
        repo_findings = await analyze_repo(repo)
        findings.extend(repo_findings)

    return {"findings": findings}

@app.get("/inactive")
async def list_inactive_users():
    """List inactive collaborators (no activity in last 30 days)."""
    inactive_users = await get_inactive_collaborators()
    return {"inactive_users": inactive_users}