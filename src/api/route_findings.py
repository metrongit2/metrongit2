from fastapi import APIRouter
from src.db.storage import Storage
from src.models.findings import Finding

router = APIRouter()
storage = Storage()

@router.get("/", response_model=list[Finding])
def get_findings():
    return storage.list_findings()
