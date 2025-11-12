from schemas import user_schemas
from typing import List
from fastapi import Depends, HTTPException, APIRouter
from database import get_db
from models import user_models
from models.user_models import User
from auth import (
    create_access_token,
    authentication,
    get_currect_user
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_


router = APIRouter(prefix='/users',tags=['Users'])


@router.get('/login/', name='login')
async def login_user(username: str, password: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username==username))
    user = result.scalar_one_or_none()

    if user is None or user.password != password:
        raise HTTPException(status_code=400,detail='Incorrect username or password')
    
    data = {
        'sub': str(user.id),
        'username': user.username,
        'email': user.email
    }

    token = create_access_token(data=data)
    return {
        'access_token': token,
        'token_type': 'Bearer'
    }



@router.post('/', response_model=user_schemas.UserRead, status_code=201, name='create-user')
async def create_user(user: user_schemas.UserCreate , db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(or_(user_models.User.email==user.email,user_models.User.username==user.username)))
    db_user = result.scalar_one_or_none()
    if db_user:
        raise HTTPException(status_code=400,detail='Email or Username already exists.')
    user = User(username=user.username,email=user.email,password=user.password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get('/', response_model=List[user_schemas.UserRead], name='list-user')
async def list_user(auth_user: User = Depends(authentication),db : AsyncSession = Depends(get_db)
                    ):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.get('/{user_id}/', response_model=user_schemas.UserRead, name='detail-user')
async def detail_user(user_id: int ,
                      auth_user: User = Depends(authentication),
                      db : AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id==user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail='The user not found')
    return user 


@router.put('/{user_id}/', response_model=user_schemas.UserRead, name='update-user')
async def edit_user(user_id: int , user : user_schemas.UserEdit , db : AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id==user_id))
    user_obj = result.scalar_one_or_none()


    if not user_obj:
        raise HTTPException(status_code=404,detail='The user not found')

    for field, value in user.dict(exclude_unset=True).items():
        setattr(user_obj,field,value)

    await db.commit()
    await db.refresh(user_obj)
    return user_obj


@router.delete('/{user_id}/',status_code=204, name='delete-user')
async def delete_user(user_id: int , db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id==user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail='The user not found')

    await db.delete(user)
    await db.commit()
    return True
  