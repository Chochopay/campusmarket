from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.categories.schemas import CategoryResponse
from app.database import get_db
from app.categories.models import Category
from typing import List

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    categories = db.execute(select(Category)).scalars().all()
    return categories
