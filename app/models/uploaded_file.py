from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database.base import Base


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)

    file_name = Column(String, nullable=False)

    file_path = Column(String, nullable=False)

    file_type = Column(String, nullable=False)

    file_size = Column(Integer, nullable=False)

    uploaded_by = Column(String, nullable=False)

    uploaded_at = Column(DateTime, default=datetime.utcnow)