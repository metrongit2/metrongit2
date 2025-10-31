from pydantic import BaseModel
from typing import Optional, Dict, Any

class Finding(BaseModel):
    id: str
    type: str                      # e.g., misconfiguration | secret | inactive_user | risky_pr
    description: str
    resource: str                  # e.g., org/repo, repo/path, collaborator:username
    severity: str                  # low|medium|high|critical
    timestamp: str                 # ISO8601
    status: str = "open"           # open|remediated
    details: Optional[Dict[str, Any]] = {}
