from typing import List, TYPE_CHECKING
from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String
)

if TYPE_CHECKING:
    from models.book_models import Book


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column( primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), index=True, unique=True)
    email: Mapped[str | None] = mapped_column(String(120), unique=True)
    password: Mapped[str] = mapped_column(String(200))

    books: Mapped[List['Book']] = relationship('Book', back_populates="author")
