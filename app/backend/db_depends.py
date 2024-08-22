from .db import AsyncSession


async def get_db():
    db = AsyncSession()
    try:
        yield db
    finally:
        await db.close()
