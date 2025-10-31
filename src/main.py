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
    repos = await get_repos()
    all_findings = []

    for repo in repos:
        # 🧩 Scan for repo-level misconfigurations
        repo_findings = await analyze_repo(repo)

        # 🧩 Scan for inactive collaborators
        inactive_users = await get_inactive_collaborators(repo)

        # Combine results
        all_findings.extend(repo_findings)
        all_findings.extend(inactive_users)

    return {"findings": all_findings}