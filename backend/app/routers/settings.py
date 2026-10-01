from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.repositories import settings_repo

router = APIRouter()

class SettingsUpdate(BaseModel):
    overlap: float

@router.get("/settings")
def settings(): return settings_repo.get_all()

@router.post("/settings")
def update_settings(body: SettingsUpdate):
    try:
        settings_repo.set_overlap(body.overlap)
    except ValueError:
        raise HTTPException(status_code=422, detail="overlap must be positive")
    return settings_repo.get_all()
