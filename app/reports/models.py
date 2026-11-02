from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Index
from app.database import Base
from typing import Optional

class Report(Base):
    __tablename__="reports"
    __table_args__ = (Index(
        "uq_report_user_listing",
        "user_id",
        "listing_id",
        unique=True
    ),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))
    reason: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column(nullable=False, default="pending")
    resolution: Mapped[Optional[str]] = mapped_column(nullable=True)
