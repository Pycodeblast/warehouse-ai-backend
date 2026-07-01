from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.database.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    sku = Column(String, unique=True, nullable=False)

    quantity = Column(Integer, default=0)

    price = Column(Float, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

