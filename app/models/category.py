from app.backend.bd import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy import relationship


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)


