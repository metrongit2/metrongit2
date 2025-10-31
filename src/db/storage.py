import json
import os
from typing import List, Dict
from src.utils.config import settings
from src.utils.logger import logger

class Storage:
    def __init__(self, path: str = None):
        self.path = path or settings.findings_db
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w") as fh:
                json.dump([], fh)

    def list_findings(self) -> List[Dict]:
        with open(self.path, "r") as fh:
            try:
                return json.load(fh)
            except Exception:
                return []

    def save_findings(self, findings: List[Dict]) -> None:
        with open(self.path, "w") as fh:
            json.dump(findings, fh, indent=2)
        logger.info(f"Saved {len(findings)} findings to {self.path}")

    def add_findings(self, new_findings: List[Dict]) -> None:
        data = self.list_findings()
        data.extend(new_findings)
        self.save_findings(data)

    def update_status(self, finding_id: str, status: str) -> None:
        data = self.list_findings()
        for f in data:
            if f.get("id") == finding_id:
                f["status"] = status
        self.save_findings(data)
        logger.info(f"Updated finding {finding_id} => {status}")

    def clear(self) -> None:
        self.save_findings([])
