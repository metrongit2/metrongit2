import httpx
from datetime import datetime, timedelta
from src.utils.config import settings

GITHUB_API = "https://api.github.com"

async def get_inactive_collaborators(days: int = 30):
    """Find org members with no public GitHub activity in the last 'days' days."""
    headers = {"Authorization": f"token {settings.github_token}"}
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    inactive_users = []

    async with httpx.AsyncClient() as client:
        # Get all members of the org
        members_url = f"{GITHUB_API}/orgs/{settings.github_org}/members"
        members = (await client.get(members_url, headers=headers)).json()

        # For each member, check latest public event
        for member in members:
            username = member["login"]
            events_url = f"{GITHUB_API}/users/{username}/events/public"
            events = (await client.get(events_url, headers=headers)).json()

            # Skip users with no events
            if not events:
                inactive_users.append({"user": username, "status": "inactive", "last_activity": "N/A"})
                continue

            # Find latest event timestamp
            latest_event = max(
                datetime.fromisoformat(e["created_at"].replace("Z", "+00:00"))
                for e in events if "created_at" in e
            )

            if latest_event < cutoff_date:
                inactive_users.append({
                    "user": username,
                    "status": "inactive",
                    "last_activity": latest_event.isoformat()
                })

    return inactive_users