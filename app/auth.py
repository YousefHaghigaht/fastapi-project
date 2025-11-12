from jose import jwt, JWSError, ExpiredSignatureError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.user_models import User
from env_data import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM
)


SECRET_KEY = JWT_SECRET_KEY

ALGORITHM = JWT_ALGORITHM

authentication = HTTPBearer()

def create_access_token(data: dict, expire_minutes: int = 30):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode.update({'exp': expire})
    encode_jwt = jwt.encode(to_encode,SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

async def get_currect_user(
        credentials: HTTPAuthorizationCredentials = Depends(authentication),
        db: AsyncSession = Depends(get_db)
        ):
    token = credentials.credentials
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,  
        detail= 'Invalid authentication credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )    
    try:
        payload = jwt.decode(token , SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get('sub')
        if user_id is None:
            raise auth_error
    except JWSError:
        raise auth_error
    
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=' Signature has expired.'
        )
    
    # find user from database
    result = await db.execute(select(User).where(User.id==user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise auth_error
    
    return user
