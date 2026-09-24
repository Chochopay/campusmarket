from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from app.database import Base
from typing import List


class DealRequest(Base):
    __tablename__="deal_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default="pending")
    text: Mapped[str] = mapped_column(nullable=False)

    messages: Mapped[List["Message"]] = relationship(back_populates="request")