from datetime import datetime

async def analyze_repo(repo: dict) -> list[dict]:
    """Analyze a single GitHub repository for basic misconfigurations."""
    findings = []

    name = repo.get("name", "unknown-repo")
    visibility = "public" if not repo.get("private") else "private"
    default_branch = repo.get("default_branch", "main")

    # Rule 1: Check for public visibility
    if visibility == "public":
        findings.append({
            "id": repo.get("id"),
            "type": "misconfiguration",
            "resource": name,
            "description": "Repository is public — may expose code or secrets.",
            "severity": "medium",
            "timestamp": datetime.utcnow().isoformat()
        })

    # Rule 2: Add general repo info
    findings.append({
        "id": repo.get("id"),
        "type": "info",
        "resource": name,
        "description": f"Scanned repo: {visibility}, default branch: {default_branch}",
        "severity": "low",
        "timestamp": datetime.utcnow().isoformat()
    })

    return findings
