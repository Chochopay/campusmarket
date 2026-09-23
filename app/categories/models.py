from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.database import Base

class Category(Base):
    __tablename__="categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
