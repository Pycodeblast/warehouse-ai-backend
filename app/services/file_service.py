import os
import shutil
from fastapi import UploadFile
from app.core.logger import logger

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def save_file(file: UploadFile):
    logger.info(f"Uploading file: {file.filename}")

    # Prevent filename collision (important in real systems)
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"File uploaded successfully: {file.filename}")

        return file.filename

    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise