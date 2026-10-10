from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.database import get_db
from app.auth.dependencies import get_current_user

from app.deal_requests.schemas import DealRequestCreate, DealRequestResponse

from app.users.models import User
from app.listings.models import Listing
from app.deal_requests.models import DealRequest



router = APIRouter(tags=["requests"])


@router.post("/listings/{listing_id}/requests", response_model=DealRequestResponse)
def create_request(data: DealRequestCreate,
                   listing_id: int,
                   current_user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)
                   ):
    listing = db.execute(select(Listing).where(Listing.id == listing_id)).scalar_one_or_none()
    if not listing:
        raise HTTPException(
            status_code=404,
            detail="Такого обьявления нет"
        )
    if listing.status != "published":
        raise HTTPException(
            status_code=409,
            detail="Вы не можете оставить заявку на неопубликованное обьявление"
        )

    if listing.user_id == current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Вы не можете оставить заявку на свое обьявление"
        )
    request = db.execute(select(DealRequest).where(DealRequest.buyer_id == current_user.id,
                                                   DealRequest.listing_id == listing_id,
                                                   DealRequest.status == "pending")).scalar_one_or_none()
    if request:
        raise HTTPException(
            status_code=409,
            detail="Вы уже оставляли заявку на это обьявление"
        )
    new_request = DealRequest(
        buyer_id=current_user.id,
        listing_id=listing_id,
        text=data.text
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return new_request


@router.get("/listings/{listing_id}/requests", response_model=List[DealRequestResponse])
def get_requests(listing_id: int,
                 current_user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):

    listing = db.execute(select(Listing).where(Listing.id == listing_id)).scalar_one_or_none()
    if not listing:
        raise HTTPException(
            status_code=404,
            detail="Такого обьявления нет"
        )
    if listing.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Это не выше обьявление"
        )
    requests = db.execute(select(DealRequest).where(DealRequest.listing_id == listing_id)).scalars().all()
    return requests


@router.get("/requests/my", response_model=List[DealRequestResponse])
def get_my_requests(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    requests = db.execute(select(DealRequest).where(DealRequest.buyer_id == current_user.id)
                          ).scalars().all()
    return requests


@router.post("/requests/{request_id}/accept")
def accept_request(request_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    request = db.execute(select(DealRequest).where(DealRequest.id == request_id)).scalar_one_or_none()
    if not request:
        raise HTTPException(
            status_code=404,
            detail="Такой заявки нет"
        )
    listing = db.execute(select(Listing).where(Listing.id == request.listing_id)).scalar_one_or_none()
    if not listing:
        raise HTTPException(
            status_code=404,
            detail="Такого обьявления нет"
        )
    if listing.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Это не ваше обьявление"
        )
    if request.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="Эта заявка уже принята либо не актуальна"
        )
    buyer = db.execute(select(User).where(User.id == request.buyer_id)).scalar_one_or_none()
    if not buyer:
        raise HTTPException(
            status_code=404,
            detail="Такого юзера больше нет"
        )
    if listing.status != "published":
        raise HTTPException(
            status_code=409,
            detail="Это обьявление не опубликовано или уже завершено"
        )

    request.status = "accepted"
    listing.status = "reserved"
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Вы не можете принять новую заявку пока старая еще актуальна"
        )
    db.refresh(request)
    return {"Успешно": f"Заявка пользователя: {buyer.username} принята"}


@router.patch("/requests/{request_id}/cancel")
def cancel_request(request_id: int,
                   current_user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    request = db.execute(select(DealRequest).where(DealRequest.id == request_id)).scalar_one_or_none()
    if not request:
        raise HTTPException(
            status_code=404,
            detail="Такой заявки нет"
        )

    listing = db.execute(select(Listing).where(Listing.id == request.listing_id)).scalar_one_or_none()
    if not listing:
        raise HTTPException(
            status_code=404,
            detail="Такого обьявления нет"
        )
    is_buyer = request.buyer_id == current_user.id
    is_seller = listing.user_id == current_user.id

    if not is_buyer and not is_seller:
        raise HTTPException(
            status_code=403,
            detail="Вы не участник этой сделки"
        )
    if request.status in ("cancelled", "completed"):
        raise HTTPException(
            status_code=409,
            detail="Заявка уже не актуальна"
        )
    elif request.status == "pending" and (is_buyer or is_seller):
        request.status = "cancelled"

    elif request.status ==  "accepted" and (is_buyer or is_seller):
        request.status = "cancelled"
        listing.status = "published"

    db.commit()
    return {"Успешно": f"Заявка отклонена"}


