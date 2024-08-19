from fastapi import APIRouter, Depends, status, HTTPException
from slugify import slugify
from typing import Annotated

from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update

from app.backend.db_depends import get_db
from app.models import *
from app.schemas import CreateProduct

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/")
async def all_products(db: Annotated[Session, Depends(get_db)]):
    products = db.scalars(select(Product).where(Product.is_active == True, Product.stock > 0)).all()
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no products")
    return products


@router.post('/create')
async def create_product(db: Annotated[Session, Depends(get_db)], create_product: CreateProduct):
    db.execute(insert(Product).values(name=create_product.name,
                                      description=create_product.description,
                                      price=create_product.price,
                                      image_url=create_product.image_url,
                                      stock=create_product.stock,
                                      category_id=create_product.category_id,
                                      slug=slugify(create_product.name)))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }



@router.get('/{category_slug}')
async def product_by_category(db: Annotated[Session, Depends(get_db)], category_slug: str):
    category = db.execute(select(Category).where(Category.slug == category_slug)).scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    subcategories = db.scalars(select(Category).where(Category.parent_id == category.id)).all()
    categories_and_subcategories = [category.id] + [i.id for i in subcategories]
    products_category = db.scalars(
        select(Product).where(Product.category_id.in_(categories_and_subcategories),
                                          Product.is_active == True, Product.stock > 0)).all()

    return products_category









@router.get('/detail/{product_slug}')
async def product_detail(product_slug: str):
    pass


@router.put('/detail/{product_slug}')
async def update_product(product_slug: str):
    pass


@router.delete('/delete')
async def delete_product(product_id: int):
    pass
