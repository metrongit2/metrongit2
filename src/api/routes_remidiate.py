from fastapi import APIRouter, HTTPException, Query
from src.db.storage import Storage
from src.services.github_client import remove_collaborator, list_collaborators
from src.utils.logger import logger

router = APIRouter()
storage = Storage()

@router.post("/{finding_id}")
async def remediate(finding_id: str, confirm: bool = Query(False)):
    findings = storage.list_findings()
    target = next((f for f in findings if f["id"] == finding_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Finding not found")

    if target["type"] != "inactive_user":
        raise HTTPException(status_code=400, detail="Only inactive_user remediation supported")

    username = target.get("details", {}).get("username") or target.get("resource")
    owner_repo = target.get("details", {}).get("repo")  # optional repo context

    if not username:
        raise HTTPException(status_code=400, detail="No username found in finding details")

    # If we have repo context, remove from that repo, otherwise attempt to remove from all repos
    if not confirm:
        return {"status": "dry-run", "message": f"Would remove collaborator {username}. Add confirm=true to actually remove."}

    # Attempt removal across repos if owner_repo missing
    removed = False
    if owner_repo:
        owner, repo = owner_repo.split("/")
        ok = await remove_collaborator(owner, repo, username)
        removed = removed or ok
    else:
        # remove from all repos in org where they are collaborator (best-effort)
        # fetch list of repos and collaborators per repo (synchronous for brevity)
        from src.services.github_client import list_org_repos, list_collaborators
        repos = await list_org_repos()
        for r in repos:
            owner = r.get("owner", {}).get("login")
            repo_name = r.get("name")
            try:
                collabs = await list_collaborators(owner, repo_name)
                if any(c.get("login") == username for c in collabs):
                    ok = await remove_collaborator(owner, repo_name, username)
                    removed = removed or ok
            except Exception:
                continue

    if removed:
        storage.update_status(finding_id, "remediated")
        logger.info(f"Remediated finding {finding_id} by removing {username}")
        return {"status": "remediated", "username": username}
    else:
        raise HTTPException(status_code=500, detail="Failed to remove collaborator")
