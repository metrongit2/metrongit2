from datetime import datetime, timedelta
import httpx
from src.utils.config import settings

GITHUB_API = "https://api.github.com"

async def get_inactive_collaborators(repo):
    """
    Detect inactive collaborators in a given repo.
    A collaborator is inactive if no commits in the last 30 days.
    """
    owner = settings.github_org
    repo_name = repo.get("name")
    headers = {"Authorization": f"token {settings.github_token}"}

    async with httpx.AsyncClient() as client:
        # 1️⃣ Get collaborators
        collab_url = f"{GITHUB_API}/repos/{owner}/{repo_name}/collaborators"
        collab_resp = await client.get(collab_url, headers=headers)
        collab_resp.raise_for_status()
        collaborators = collab_resp.json()

        findings = []
        since_date = (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z"

        for user in collaborators:
            username = user["login"]

            # 2️⃣ Check for commits by this user
            commits_url = (
                f"{GITHUB_API}/repos/{owner}/{repo_name}/commits"
                f"?author={username}&since={since_date}"
            )
            commits_resp = await client.get(commits_url, headers=headers)

            if commits_resp.status_code == 200 and len(commits_resp.json()) == 0:
                # 3️⃣ Mark inactive
                findings.append({
                    "id": f"{repo_name}-{username}",
                    "type": "user_inactivity",
                    "resource": username,
                    "repo": repo_name,
                    "description": f"User '{username}' inactive for 30+ days",
                    "severity": "low",
                    "timestamp": datetime.utcnow().isoformat(),
                })

        return findings