from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Index
from app.database import Base

class Favorite(Base):
    __tablename__="favorites"
    __table_args__ = (Index(
        "uq_user_id_for_listing",
        "listing_id",
        "user_id",
        unique=True
    ),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), nullable=False)