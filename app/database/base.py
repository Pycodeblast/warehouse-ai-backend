from sqlalchemy.orm import DeclarativeBase
from app.database.database import engine

class Base(DeclarativeBase):
    pass

def create_db_tables():
    from app.models.user import User  # import models here

    Base.metadata.create_all(bind=engine)