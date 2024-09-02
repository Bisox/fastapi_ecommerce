from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from typing import Annotated

from app.backend.db_depends import get_db
from reviews import Review

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get('/')
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews_query = select(Review).where(Review.is_active)
    results = await db.scalars(reviews_query)
    reviews = results.all()
    return reviews


