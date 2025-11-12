from typing import Optional
from pydantic import BaseModel, field_validator, Field
from fastapi import Depends
from sqlalchemy import select


class BaseUser(BaseModel):
    username: str
    email: str

    @field_validator('username')
    def validate_username(cls, username):
        if username == 'admin':
            raise ValueError('You cant using from admin to username')
        return username

class UserCreate(BaseUser):
    password: str


class UserRead(BaseUser):
    id: int

    model_config = {'from_attributes': True}


class UserEdit(BaseModel):
    username: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
