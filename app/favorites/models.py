from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.database import Base

class Favorite(Base):
    __tablename__="favorites"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), nullable=False)