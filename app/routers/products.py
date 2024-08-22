from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from slugify import slugify
from sqlalchemy import insert, select, update, and_
from sqlalchemy.orm import Session

from app.backend.db_depends import get_db
from app.models import *
from app.schemas import CreateProduct

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/")
async def all_products(db: Annotated[Session, Depends(get_db)]):
    is_active_condition = Product.is_active
    stock_condition = Product.stock > 0

    product = select(Product).where(and_(is_active_condition, stock_condition))
    result = db.scalars(product).all()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no products")
    return result


@router.post('/create')
async def create_product(db: Annotated[Session, Depends(get_db)], create_product: CreateProduct):
    product_create = insert(Product).values(name=create_product.name,
                                            description=create_product.description,
                                            price=create_product.price,
                                            image_url=create_product.image_url,
                                            stock=create_product.stock,
                                            category_id=create_product.category_id,
                                            slug=slugify(create_product.name))
    db.execute(product_create)

    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.get('/{category_slug}')
async def product_by_category(db: Annotated[Session, Depends(get_db)], category_slug: str):
    category_query = select(Category).where(Category.slug == category_slug)
    category = db.execute(category_query).scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Category not found")

    subcategories_query = select(Category).where(Category.parent_id == category.id)
    subcategories = db.scalars(subcategories_query).all()

    categories_and_subcategories = [category.id] + [i.id for i in subcategories]

    products_query = select(Product).where(Product.category_id.in_(categories_and_subcategories),
                                           Product.is_active, Product.stock > 0)

    products_category = db.scalars(products_query).all()

    return products_category


@router.get('/detail/{product_slug}')
async def product_detail(db: Annotated[Session, Depends(get_db)], product_slug: str):
    product_query = select(Product).where(Product.slug == product_slug, Product.is_active, Product.stock > 0)
    product = db.scalar(product_query)

    if not product:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no product'
        )
    return product


@router.put('/detail/{product_slug}')
async def update_product(db: Annotated[Session, Depends(get_db)], product_slug: str,
                         update_product_model: CreateProduct):

    product_query = select(Product).where(Product.slug == product_slug)
    product_update = db.scalar(product_query)

    if product_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    update_query = (update(Product).where(Product.slug == product_slug)
                    .values(name=update_product_model.name,
                            description=update_product_model.description,
                            price=update_product_model.price,
                            image_url=update_product_model.image_url,
                            stock=update_product_model.stock,
                            category_id=update_product_model.category_id,
                            slug=slugify(update_product_model.name)))

    db.execute(update_query)
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product update is successful'
    }


@router.delete('/delete')
async def delete_product(db: Annotated[Session, Depends(get_db)], product_id: int):

    product_delete = db.scalar(select(Product).where(Product.id == product_id))

    if product_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    update_query = update(Product).where(Product.id == product_id).values(is_active=False)

    db.execute(update_query)
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product delete is successful'
    }
