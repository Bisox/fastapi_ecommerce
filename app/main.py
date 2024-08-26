from fastapi import FastAPI
from app.routers import category, products, auth


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


app.include_router(category.router)
app.include_router(products.router)
app.include_router(auth.router)