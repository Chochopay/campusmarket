from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.users.models import User
from app.listings.models import Listing
from app.favorites.models import Favorite

from app.favorites.schemas import FavoriteAdd, FavoriteResponse
from app.listings.schemas import ListingResponse
from app.common.pagination_scheme import Pagination

from app.auth.dependencies import get_current_user
from app.database import get_db

from typing import List, Optional


router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.post("/", response_model=FavoriteResponse)
def add_listing_to_favorites(data: FavoriteAdd,
                             current_user: User = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    listing = db.execute(select(Listing).where(Listing.id == data.listing_id)).scalar_one_or_none()
    if not listing:
        raise HTTPException(
            status_code=404,
            detail="Такого объявления нет"
        )
    if current_user.id == listing.user_id:
        raise HTTPException(
            status_code=403,
            detail="Вы не можете добавить свое объявление в Избранное"
        )
    is_favorite_listing = db.execute(select(Favorite).where(Favorite.user_id == current_user.id,
                                                            Favorite.listing_id == listing.id)).scalar_one_or_none()
    if is_favorite_listing:
        raise HTTPException(
            status_code=409,
            detail="Объявление уже добавлено в Избранное"
        )
    if listing.status not in ["published", "reserved"]:
        raise HTTPException (
            status_code=400,
            detail="Статус объявление не соответствует требованиям"
        )

    new_favorite = Favorite(
        user_id=current_user.id,
        listing_id=listing.id
    )
    try:
        db.add(new_favorite)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Объявление уже добавлено в Избранное"
        )
    db.refresh(new_favorite)
    return new_favorite


@router.get("/", response_model=Pagination[ListingResponse])
def get_my_favorites(limit: int = Query(default=20, ge=1, le=100),
                     offset: int = Query(default=0, ge=0),
                    current_user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):

    query = select(Listing).where(Listing.id.in_(
                                        select(Favorite.listing_id).where(
                                            Favorite.user_id == current_user.id)),
                                            Listing.status != "hidden").order_by(Listing.id.desc())
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    query = query.limit(limit).offset(offset)
    favorites = db.execute(query).scalars().all()

    return {"items": favorites, "total": total, "limit": limit, "offset": offset}


@router.delete("/{listing_id}")
def delete_listing_from_favorite(listing_id: int,
                                 current_user: User = Depends(get_current_user),
                                 db: Session = Depends(get_db)):
    is_favorite_listing = db.execute(select(Favorite).where(Favorite.user_id == current_user.id,
                                                                        Favorite.listing_id == listing_id
                                                            )).scalar_one_or_none()
    if not is_favorite_listing:
        raise HTTPException (
            status_code=404,
            detail="Такого объявления нет у вас в Избранных"
        )
    db.delete(is_favorite_listing)
    db.commit()
    return {"Удалено": "Объявление удалено из Избранных"}