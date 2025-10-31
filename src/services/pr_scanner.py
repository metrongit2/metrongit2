from typing import List, Dict
from src.services.github_client import list_pull_requests, get_commit_history, get_file_contents
from datetime import datetime

SENSITIVE_PATHS = [".github/", "infra/", "deploy/", "secrets/", "configs/"]

async def analyze_prs(owner: str, repo: str) -> List[Dict]:
    findings = []
    prs = await list_pull_requests(owner, repo, state="open")
    for pr in prs:
        number = pr.get("number")
        title = pr.get("title")
        user = pr.get("user", {}).get("login")
        # best-effort fetch additions/deletions via PR details
        additions = pr.get("additions") or 0
        deletions = pr.get("deletions") or 0
        reviewers = pr.get("requested_reviewers", [])
        files_url = pr.get("_links", {}).get("self", {}).get("href")  # fallback
        # classify
        size = additions + deletions
        risky = False
        reasons = []
        if size > 500:
            risky = True
            reasons.append(f"Large diff ({size} changes)")
        if not reviewers:
            risky = True
            reasons.append("No reviewers requested")
        # check changed files for sensitive paths: GitHub PR API file list would be better, but use contents heuristic
        # (lightweight) — mark risky if title or body references infra or if repo has those paths
        # (This is a lightweight heuristic for hackathon)
        body = pr.get("body") or ""
        if any(p in (pr.get("title","") + body) for p in SENSITIVE_PATHS):
            risky = True
            reasons.append("PR touches sensitive path (heuristic)")
        if risky:
            findings.append({
                "id": f"pr-{repo}-{number}",
                "type": "risky_pr",
                "description": f"PR #{number} by {user}: {', '.join(reasons)}",
                "resource": f"{owner}/{repo}",
                "severity": "medium" if "No reviewers" in reasons else "high",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "details": {"pr_number": number, "reasons": reasons}
            })
    return findings
