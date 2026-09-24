from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.database import Base
from typing import Optional

class Report(Base):
    __tablename__="reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))
    reason: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column(nullable=False, default="pending")
    resolution: Mapped[Optional[str]] = mapped_column(nullable=True)
