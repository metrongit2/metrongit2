import httpx
from datetime import datetime, timedelta
from src.utils.config import settings

GITHUB_API = "https://api.github.com"

async def get_inactive_collaborators(days: int = 30):
    """
    Detect inactive collaborators in the org — no recent commits within 'days' days.
    """
    headers = {"Authorization": f"token {settings.github_token}"}
    inactive_users = []
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    async with httpx.AsyncClient() as client:
        # 1️⃣ Get all members of the organization
        members_url = f"{GITHUB_API}/orgs/{settings.github_org}/members"
        members_resp = await client.get(members_url, headers=headers)
        members_resp.raise_for_status()
        members = members_resp.json()

        for member in members:
            username = member["login"]

            # 2️⃣ Get user events (pushes, commits, PRs)
            events_url = f"{GITHUB_API}/users/{username}/events"
            events_resp = await client.get(events_url, headers=headers)
            if events_resp.status_code != 200:
                continue

            events = events_resp.json()
            last_activity = None
            for e in events:
                if e.get("created_at"):
                    ts = datetime.fromisoformat(e["created_at"].replace("Z", "+00:00"))
                    if not last_activity or ts > last_activity:
                        last_activity = ts

            # 3️⃣ Mark user as inactive if no recent activity
            if not last_activity or last_activity < cutoff_date:
                inactive_users.append({
                    "user": username,
                    "last_activity": last_activity.isoformat() if last_activity else "N/A",
                    "status": "inactive"
                })

    return inactive_users