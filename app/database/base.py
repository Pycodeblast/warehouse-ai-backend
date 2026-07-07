from sqlalchemy.orm import DeclarativeBase
from app.database.database import engine


class Base(DeclarativeBase):
    pass


# IMPORT ALL MODELS HERE
from app.models.user import User
from app.models.product import Product
from app.models.activity_log import ActivityLog


def create_db_tables():
    print("Registered tables:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)