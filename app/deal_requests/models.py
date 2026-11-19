from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Index, text
from app.database import Base
from typing import List


class DealRequest(Base):
    __tablename__="deal_requests"
    __table_args__ = (
        Index(
            "uq_one_accept_per_listing",
            "listing_id",
            unique=True,
            sqlite_where=text("status='accepted'"),
            postgresql_where=text("status='accepted'")
        ),)

    id: Mapped[int] = mapped_column(primary_key=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default="pending")
    text: Mapped[str] = mapped_column(nullable=False)

    messages: Mapped[List["Message"]] = relationship(back_populates="request")

    buyer: Mapped["User"] = relationship("User")
    listing: Mapped["Listing"] = relationship("Listing")

    @property
    def buyer_username(self) -> str:
        return self.buyer.username

    @property
    def listing_name(self) -> str:
        return self.listing.name