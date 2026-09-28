from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.listings.schemas import ListingCreate, ListingResponse
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.users.models import User
from app.listings.models import Listing
from app.categories.models import Category

#Listings:

#GET /listings (с query-фильтрами)
#POST /listings
#PATCH /listings/{id}
#POST /listings/{id}/complete
#POST /listings/{id}/images
#DELETE /listings/{id}/images/{image_id}


router = APIRouter(prefix="/listings", tags=["listings"])

@router.post("/", response_model=ListingResponse)
def create_listing(
        data: ListingCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)):

    is_category = db.execute(select(Category).where(Category.id==data.category_id)).scalar_one_or_none()
    if not is_category:
        raise HTTPException(
            status_code=404,
            detail="Такой категории не существует"
        )

    new_listing = Listing(
        name=data.name,
        description=data.description,
        condition=data.condition,
        mode=data.mode,
        price=data.price,
        user_id=current_user.id,
        category_id=data.category_id
    )
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)
    return new_listing

@router.get("/{id}", response_model=ListingResponse)
def get_listing_by_id(id: int, db: Session = Depends(get_db)):
    listing = db.execute(select(Listing).where(Listing.id == id)).scalar_one_or_none()
    if not listing:
        raise HTTPException(
            status_code = 404,
            detail="Такого обьявления нет"
        )
    return listing
