from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, insert

from app.models.user import User
from app.schemas import CreateUser
from app.backend.db_depends import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from passlib.context import CryptContext

router = APIRouter(prefix='/auth', tags=['auth'])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.post('/')
async def create_user(db: Annotated[AsyncSession, Depends(get_db)], create_user: CreateUser):
    await db.execute(insert(User).values(first_name=create_user.first_name,
                                         last_name=create_user.last_name,
                                         username=create_user.username,
                                         email=create_user.email,
                                         hashed_password=bcrypt_context.hash(create_user.password),
                                         ))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }