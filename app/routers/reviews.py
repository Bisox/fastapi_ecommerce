
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.dialects.mysql import insert

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, and_

from typing import Annotated


from app.backend.db_depends import get_db
from app.models import *
from app.services.auth_helpers import get_current_user
from app.schemas import CreateReview

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
            'review': review.comment,
            'grade': rating.grade if rating else None
        })

    return result if result else {'message': 'No reviews found'}


@router.post('create')
async def add_review(db: Annotated[AsyncSession, Depends(get_db)],
                     get_user: Annotated[dict, Depends(get_current_user)],
                     create_review: CreateReview,
                     product_slug: str,):
    if get_user.get('is_customer'):

        product_query = select(Product).where(Product.slug == product_slug)
        product = await db.scalar(product_query)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Product not found")

        rating_create = insert(Rating).values(grade=create_review.grade,
                                              user_id=get_user.get('id'),
                                              product_id=product.id
        ).returning(Rating.id)

        rating_result = await db.execute(rating_create)
        rating_id = rating_result.scalar()

        review_create = insert(Review).values(user_id=get_user.get('id'),
                                              product_id=product.id,
                                              rating_id=rating_id,
                                              comment=create_review.comment
        )

        await db.execute(review_create)
        await db.commit()

        ratings_query = select(Rating.grade).where(Rating.product_id == product.id)
        ratings = await db.scalars(ratings_query)
        ratings_list = ratings.all()

        average_rating = sum(ratings_list) / len(ratings_list)


        update_product = product.__table__.update().where(Product.id == product.id).values(rating=average_rating)
        await db.execute(update_product)
        await db.commit()

        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )



@router.delete('/delete/{product_slug}')
async def delete_review(db: Annotated[AsyncSession,
                        Depends(get_db)], product_slug: str,
                        get_user: Annotated[dict, Depends(get_current_user)]):

    product_query = select(Product).where(Product.slug == product_slug)
    product = await db.scalar(product_query)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found')

    if not get_user.get('is_admin'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )

    review_query = select(Review).where(Review.product_id == product.id)
    reviews = await db.scalars(review_query)

    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No reviews found for this product'
        )

    for review in reviews:
        update_rating_query = update(Rating).where(Rating.id == review.rating_id).values(is_active=False)
        await db.execute(update_rating_query)

        update_review_query = update(Review).where(Review.id == review.id).values(is_active=False)
        await db.execute(update_review_query)

    await db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product reviews and ratings deactivation is successful'
    }



