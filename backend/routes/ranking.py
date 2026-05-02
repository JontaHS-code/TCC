from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Politico

router = APIRouter(prefix="/ranking", tags=["Ranking"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/irep")
def ranking_irep(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Politico).order_by(Politico.irep_score.desc()).limit(limit).all()