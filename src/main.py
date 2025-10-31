from fastapi import FastAPI
from src.services.github_client import get_repos
from src.services.repo_scanner import analyze_repo
from src.services.user_scanner import get_inactive_collaborators

app = FastAPI(title="GitSafeOps")

@app.get("/")
def home():
    return {"message": "GitSafeOps API running"}


@app.get("/scan")
async def scan_repos():
    """🔍 Scan organization repositories for misconfigurations."""
    repos = await get_repos()
    all_findings = []

    for repo in repos:
        repo_findings = await analyze_repo(repo)
        all_findings.extend(repo_findings)

    return {
        "type": "repository_scan",
        "total_findings": len(all_findings),
        "findings": all_findings
    }


@app.get("/inactive")
async def scan_inactive_users():
    """🧑‍💻 Identify inactive org members based on last 30 days of activity."""
    inactive_users = await get_inactive_collaborators()
    return {
        "type": "user_activity_scan",
        "total_inactive": len(inactive_users),
        "inactive_users": inactive_users
    }
