from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.listings.schemas import ListingCreate, ListingResponse, ListingUpdate, ListingImageResponse
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.users.models import User
from app.listings.models import Listing, ListingImage
from app.categories.models import Category
from app.deal_requests.models import DealRequest

from typing import List, Literal, Optional
from decimal import Decimal
import os, uuid



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


@router.get("/my", response_model=List[ListingResponse])
def get_my_listings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    user_listings = db.execute(select(Listing).where(Listing.user_id == current_user.id)).scalars().all()
    return user_listings


@router.get("/{listing_id}", response_model=ListingResponse)
def get_listing_by_id(listing_id: int, db: Session = Depends(get_db)):
    listing = db.execute(select(Listing).where(Listing.id == listing_id)).scalar_one_or_none()
    if not listing:
        raise HTTPException(
            status_code = 404,
            detail="Такого обьявления нет"
        )
    return listing


@router.get("/", response_model=List[ListingResponse])
def get_listings(
        category_id: Optional[int] = None,
        condition: Optional[str] = None,
        mode: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        sort: Optional[Literal["date", "price"]] = None,
        db: Session = Depends(get_db)
):
    query = select(Listing).where(Listing.status == "published")

    if category_id is not None:
        query = query.where(Listing.category_id == category_id)

    if condition is not None:
        query = query.where(Listing.condition == condition)

    if mode is not None:
        query = query.where(Listing.mode == mode)

    if min_price is not None:
        query = query.where(Listing.price >= min_price)

    if max_price is not None:
        query = query.where(Listing.price <=max_price)

    if sort is not None:
        if sort == "price":
            query = query.order_by(Listing.price)
        elif sort == "date":
            query = query.order_by(Listing.created_at)

    return db.execute(query).scalars().all()


@router.patch("/{listing_id}", response_model=ListingResponse)
def patch_listing(
        listing_id: int,
        listing_update: ListingUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):

    listing = db.execute(select(Listing).where(Listing.id == listing_id)).scalar_one_or_none()
    if not listing:
        raise HTTPException(
            status_code=404,
            detail="Такого обьявления не существует"
        )
    if listing.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Это не выше обьявление"
        )
    if listing.status in ("reserved", "completed"):
        raise HTTPException(
            status_code=409,
            detail="Вы не можете редактировать обьявление пока оно в нынешнем статусе"
        )

    update_data = listing_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(listing, key, value)

    db.commit()
    db.refresh(listing)
    return listing


@router.post("/{listing_id}/complete", response_model=ListingResponse)
def complete_listing(listing_id: int,
                     current_user: User =  Depends(get_current_user),
                     db: Session = Depends(get_db)
                     ):
    listing = db.execute(select(Listing).where(Listing.id == listing_id)).scalar_one_or_none()

    if not listing:
        raise HTTPException(
            status_code=404,
            detail="Такого обьявления не существует"
        )
    if current_user.id != listing.user_id:
        raise HTTPException(
            status_code=403,
            detail="Это не ваше обьявление"
        )
    if listing.status != "reserved":
        raise HTTPException(
            status_code=409,
            detail="Вы не можете закрыть обьявление пока оно в нынешнем статусе"
        )
    request = db.execute(select(DealRequest).where(DealRequest.listing_id == listing_id,
                                                   DealRequest.status == "accepted")).scalar_one_or_none()
    if not request:
        raise HTTPException(
            status_code=409,
            detail="У этого обьявления нет принятого запроса"
        )

    listing.status = "completed"
    request.status = "completed"
    db.commit()
    db.refresh(listing)
    db.refresh(request)
    return listing


@router.post("/{listing_id}/images", response_model=ListingImageResponse)
async def add_images(listing_id: int, image: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    listing = db.execute(select(Listing).where(Listing.id == listing_id)).scalar_one_or_none()
    if not listing:
        raise HTTPException(
            status_code=404,
            detail="Такого обьявление не существует"
        )
    if current_user.id != listing.user_id:
        raise HTTPException(
            status_code=403,
            detail="Это не ваше обьявление"
        )
    listing_images = db.execute(select(ListingImage).where(ListingImage.listing_id == listing_id)).scalars().all()
    image_position = len(listing_images)

    if image_position > 4:
        raise HTTPException (
            status_code=409,
            detail="Вы достигли лимита фотографий"
        )

    if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException (
            status_code=409,
            detail="Формат изображения не поддерживается"
        )
    content = await image.read()
    file_size_limit = 5 * 1024 * 1024

    if len(content) >= file_size_limit:
        raise HTTPException(
            status_code=409,
            detail="Размер изображения превышает разрешенный лимит"
        )
    unique_filename = f"{uuid.uuid4()}_{image.filename}"

    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{unique_filename}"
    with open(file_path, "wb") as f:
        f.write(content)

    new_image = ListingImage(
        img_file=file_path,
        listing_id=listing_id,
        position=image_position
    )
    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return new_image


@router.delete("/{listing_id}/images/{image_id}")
def delete_image(listing_id: int,
                 image_id: int,
                 current_user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)
                 ):
    listing = db.execute(select(Listing).where(Listing.id == listing_id)).scalar_one_or_none()

    if not listing:
        raise HTTPException(
            status_code=404,
            detail="Такого обьявления не существует"
        )
    if current_user.id != listing.user_id:
        raise HTTPException(
            status_code=403,
            detail="Это не ваше обьявление"
        )
    image = db.execute(select(ListingImage).where(ListingImage.listing_id == listing_id,
                                                  ListingImage.id == image_id)).scalar_one_or_none()
    if not image:
        raise HTTPException(
            status_code=404,
            detail="Такого изображения нет"
        )
    try:
        os.remove(image.img_file)
    except FileNotFoundError:
        pass

    db.delete(image)
    db.commit()

    return{"detail": "Изображение удалено"}
















