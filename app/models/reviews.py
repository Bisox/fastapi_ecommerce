from datetime import datetime, timezone

from sqlalchemy import String, Boolean, Integer, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.backend.db import Base
from app.models import *

class Review(Base):

    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    rating_id = Column(Integer, ForeignKey('ratings.id'))
    comment = Column(String)
    comment_date = Column(DateTime, default=lambda: datetime.now().replace(tzinfo=None))
    is_active = Column(Boolean, default=True)

    rating = relationship('Rating', back_populates='reviews')