from typing import List
from fastapi import status, Depends, HTTPException, APIRouter
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.book_models import Book
from models.user_models import User
from auth import get_currect_user
from schemas.book_schemas import (
    BookRead,
    BookCreateEdit
)


router = APIRouter(prefix='/books',tags=['Books'])



@router.post('/', response_model=BookRead)
async def create_book(book: BookCreateEdit,
                      auth_user: User = Depends(get_currect_user),
                      db: AsyncSession = Depends(get_db)
                      ):
    result = await db.execute(select(Book).where(Book.title==book.title))
    db_book = result.scalar_one_or_none()
    if db_book:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='This title already exists')
    
    author_id = auth_user.id
    book = Book(title=book.title,
                description=book.description,
                author_id=author_id,
                )

    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book

@router.get('/',response_model=List[BookRead])
async def list_book(auth_user = Depends(get_currect_user),
                    db: AsyncSession = Depends(get_db)):
    results = await db.execute(select(Book))
    books = results.scalars().all()
    return books


@router.put('/{book_id}/', response_model=BookRead)
async def edit_book(book_id: int,
                    book: BookCreateEdit,
                    auth_user = Depends(get_currect_user),
                    db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.id==book_id))
    db_book = result.scalar_one_or_none()

    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The book not found.'
        ) 

    for field, value in book.dict(exclude_defaults=True).items():
        setattr(db_book, field, value)
    
    await db.commit()
    await db.refresh(db_book)
    return db_book


@router.delete('/{book_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int,
                      auth_user = Depends(get_currect_user),
                      db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.id==book_id))
    db_book = result.scalar_one_or_none()
    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The book not found'
        )
    await db.delete(db_book)
    await db.commit()
    return True

