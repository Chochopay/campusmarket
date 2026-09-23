from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Numeric
from decimal import Decimal
from app.database import Base
from typing import List

class Listing(Base):
    __tablename__="listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    condition: Mapped[str] = mapped_column(nullable=False)
    mode: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)

    listingimages: Mapped[List["ListingImage"]] = relationship("ListingImage", back_populates="listing", cascade="all, delete-orphan" )


class ListingImage(Base):
    __tablename__="listingimages"

    id: Mapped[int] = mapped_column(primary_key=True)
    img_file: Mapped[str] = mapped_column(nullable=False)
    listing_id: Mapped[int] = mapped_column(nullable=False)
    position: Mapped[int] = mapped_column(nullable=False)

    listing: Mapped["Listing"] = relationship(back_populates="listingimages")
