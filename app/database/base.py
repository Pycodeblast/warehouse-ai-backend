from sqlalchemy.orm import DeclarativeBase
from app.database.database import engine


class Base(DeclarativeBase):
    pass


# Import all models AFTER Base is created
from app.models.user import User
from app.models.product import Product


def create_db_tables():
    print("Registered tables:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)