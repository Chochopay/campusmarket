from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.database import Base

class Report(Base):
    __tablename__="reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    listing_id: Mapped[int] = mapped_column(ForeignKey("listing.id"))
    reason: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column(nullable=False)
    resolution: Mapped[str] = mapped_column(default="Модератор ответил на ваш репорт")
