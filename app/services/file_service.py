import os
import uuid
from datetime import datetime

import pandas as pd

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.models.product import Product
from app.core.logger import logger

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".xlsx",
    ".xls",
    ".csv",
    ".doc",
    ".docx",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".txt",
}


def get_file_type(extension: str):

    extension = extension.lower()

    if extension == ".pdf":
        return "PDF"

    elif extension in [".xls", ".xlsx"]:
        return "EXCEL"

    elif extension == ".csv":
        return "CSV"

    elif extension in [".doc", ".docx"]:
        return "WORD"

    elif extension in [".png", ".jpg", ".jpeg", ".webp"]:
        return "IMAGE"

    elif extension == ".txt":
        return "TEXT"

    return "OTHER"


def save_file(db: Session, file: UploadFile):

    logger.info(f"Uploading file: {file.filename}")

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type."
        )

    contents = file.file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Maximum upload size is 10 MB."
        )

    stored_filename = f"{uuid.uuid4()}{extension}"

    file_path = os.path.join(
        UPLOAD_FOLDER,
        stored_filename,
    )

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    logger.info("Upload completed.")

    # -----------------------------------
    # IMPORT PRODUCTS FROM EXCEL / CSV
    # -----------------------------------

    imported = 0

    if extension in [".xlsx", ".xls"]:

        df = pd.read_excel(file_path)

    elif extension == ".csv":

        df = pd.read_csv(file_path)

    else:

        df = None

    if df is not None:

        for _, row in df.iterrows():

            existing = (
                db.query(Product)
                .filter(Product.sku == row["SKU"])
                .first()
            )

            if existing:
                continue

            product = Product(
                name=row["Product Name"],
                sku=row["SKU"],
                quantity=int(row["Quantity"]),
                price=float(row["Price"]),
            )

            db.add(product)

            imported += 1

        db.commit()

    return {
        "message": "Upload successful",
        "filename": file.filename,
        "stored_filename": stored_filename,
        "file_type": get_file_type(extension),
        "content_type": file.content_type,
        "file_size": len(contents),
        "uploaded_at": datetime.now(),
        "imported_products": imported,
    }


def list_files():

    files = []

    for filename in os.listdir(UPLOAD_FOLDER):

        path = os.path.join(
            UPLOAD_FOLDER,
            filename,
        )

        extension = os.path.splitext(filename)[1]

        files.append({
            "id": filename,
            "filename": filename,
            "stored_filename": filename,
            "file_type": get_file_type(extension),
            "content_type": extension,
            "file_size": os.path.getsize(path),
            "uploaded_at": datetime.fromtimestamp(
                os.path.getctime(path)
            ),
        })

    return files


def delete_file(filename: str):

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename,
    )

    if not os.path.exists(file_path):

        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    os.remove(file_path)

    return {
        "message": "File deleted successfully."
    }