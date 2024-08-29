from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from datetime import timedelta

from app.models.user import User
from app.schemas import CreateUser
from app.backend.db_depends import get_db
from app.services.security import bcrypt_context
from app.services.auth_helpers import authenticate_user, create_access_token, get_current_user


router = APIRouter(prefix='/auth', tags=['auth'])


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

# ----------------------------------------------------------------------------------------------------------------------


@router.post('/token')
async def login(db: Annotated[AsyncSession, Depends(get_db)], form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(db, form_data.username, form_data.password)
    token = await create_access_token(user.username,
                                      user.id,
                                      user.is_admin,
                                      user.is_supplier,
                                      user.is_customer,
                                      expires_delta=timedelta(minutes=20))
    return {
        'access_token': token,
        'token_type': 'bearer'
    }


@router.get('/read_current_user')
async def read_current_user(user: dict = Depends(get_current_user)):
    return {'User': user}
