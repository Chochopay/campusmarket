from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class User(Base):
    __tablename__="users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullabe=False, default="user")
