from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class BookCreateEdit(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class BookRead(BaseModel):
    id: int
    title: str
    description: str | None
    author_id: int
    created_at: datetime
    updated_at: datetime | None
