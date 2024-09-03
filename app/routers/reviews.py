from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from typing import Annotated

from sqlalchemy.orm import joinedload

from app.backend.db_depends import get_db
from app.models import *

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get('/')
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews_query = select(Review).where(Review.is_active)
    results = await db.scalars(reviews_query)
    reviews = results.all()
    return reviews


@router.get('/{product_slug}')
async def products_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    is_active_condition = Review.is_active

    product_query = select(Product).where(Product.slug == product_slug)
    product = await db.scalar(product_query)

    reviews_query = select(Review).where(Review.product_id == product.id, is_active_condition)
    reviews = await db.scalars(reviews_query)

    result = []
    for review in reviews:

        rating_query = select(Rating).where(Rating.id == review.rating_id)
        rating = await db.scalar(rating_query)

        result.append({
            'отзыв': review.comment,
            'оценка': rating.grade if rating else None
        })

    return result if result else {'message': 'Отзывы не найдены'}

@router.post('create')
async def add_review():











