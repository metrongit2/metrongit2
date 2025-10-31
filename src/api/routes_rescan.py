from fastapi import APIRouter
from src.services.github_client import list_org_repos
from src.services.repo_scanner import get_inactive_repositories  # if used
from src.services.repo_scanner import get_inactive_repositories as _repo_inactive
from src.services.pr_scanner import analyze_prs
from src.services.secret_scanner import scan_text_for_secrets
from src.db.storage import Storage
from src.utils.logger import logger
from datetime import datetime
import uuid
import base64

router = APIRouter()
storage = Storage()

def make_finding(ftype, severity, resource, description, details=None):
    return {
        "id": str(uuid.uuid4()),
        "type": ftype,
        "severity": severity,
        "resource": resource,
        "description": description,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": "open"
    }

@router.post("/")
async def rescan():
    logger.info("Manual rescan started")
    findings = []
    repos = await list_org_repos()
    for r in repos:
        owner = r.get("owner", {}).get("login")
        repo_name = r.get("name")
        full = f"{owner}/{repo_name}"

        # Repo visibility
        if not r.get("private"):
            findings.append(make_finding("misconfiguration", "high", full, "Repository is public"))

        # Branch protection - best-effort
        default_branch = r.get("default_branch")
        try:
            # attempt protection endpoint
            bp_url = f"https://api.github.com/repos/{owner}/{repo_name}/branches/{default_branch}/protection"
            # using httpx sync call for brevity
            import httpx
            resp = httpx.get(bp_url, headers={"Authorization": f"token {storage and ''}"})  # dummy call to avoid crash
            if resp.status_code != 200:
                findings.append(make_finding("misconfiguration", "medium", full, f"No branch protection on {default_branch}"))
        except Exception:
            # can't check, add a note
            findings.append(make_finding("misconfiguration", "low", full, f"Branch protection check not available for {full}"))

        # PR analysis
        prs_findings = await analyze_prs(owner, repo_name)
        findings.extend(prs_findings)

        # Secrets: scan root contents (lightweight)
        try:
            # list contents at root
            import httpx
            cont_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents"
            resp = httpx.get(cont_url, headers={"Authorization": f"token {settings.github_token}"})
            if resp.status_code == 200:
                items = resp.json()
                for item in items:
                    if item.get("type") == "file":
                        file_resp = httpx.get(item["url"], headers={"Authorization": f"token {settings.github_token}"})
                        if file_resp.status_code == 200:
                            js = file_resp.json()
                            content = js.get("content", "")
                            if content:
                                try:
                                    raw = base64.b64decode(content).decode("utf-8", errors="ignore")
                                    secrets = scan_text_for_secrets(raw)
                                    for s in secrets:
                                        findings.append(make_finding("secret", "high", f"{full}/{item.get('path')}", f"Potential secret found", {"match": s}))
                                except Exception:
                                    continue
        except Exception:
            continue

    # persist findings
    storage.save_findings(findings)
    logger.info("Rescan complete")
    return {"status": "ok", "count": len(findings)}
