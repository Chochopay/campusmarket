from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from app.database import Base
from datetime import datetime
from app.deal_requests.models import DealRequest

class Message(Base):
    __tablename_="messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("request.id"), nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    text: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    request: Mapped["DealRequest"] = relationship(back_populate="messages")





