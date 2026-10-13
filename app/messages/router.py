from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.users.models import User
from app.listings.models import Listing
from app.deal_requests.models import DealRequest
from app.messages.models import Message

from app.messages.schemas import MessageCreate, MessageResponse

from app.auth.dependencies import get_current_user
from typing import List

router = APIRouter(tags=["messages"])



@router.post("/requests/{request_id}/messages", response_model=MessageResponse)
def create_message(request_id: int,
                   data: MessageCreate,
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

    if current_user.id not in [request.buyer_id, listing.user_id]:
        raise HTTPException(
            status_code=403,
            detail="Вы не являетесь участником сделки"
        )
    if request.status != "accepted":
        raise HTTPException(
            status_code=409,
            detail="Заявка не принята или неактуальна"
        )

    new_message = Message(
        request_id=request_id,
        sender_id=current_user.id,
        text=data.text
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


@router.get("/requests/{request_id}/messages", response_model=List[MessageResponse])
def get_messages(request_id: int,
                 current_user: User = Depends(get_current_user),
                 db: Session = Depends(get_db) ):
    request = db.execute(select(DealRequest).where(DealRequest.id == request_id)).scalar_one_or_none()
    if not request:
        raise HTTPException(
            status_code=404,
            detail="Такой заявки не существует"
        )
    listing = db.execute(select(Listing).where(Listing.id == request.listing_id)).scalar_one_or_none()
    if not listing:
        raise HTTPException(
            status_code=404,
            detail="Такого обьявления нет"
        )
    if current_user.id not in [request.buyer_id, listing.user_id]:
        raise HTTPException(
            status_code=403,
            detail="Вы не являетесь участником сделки"
        )
    messages = db.execute(select(Message).where(Message.request_id == request_id)
                          .order_by(Message.created_at)).scalars().all()
    return messages