import os
import shutil
from fastapi import UploadFile
from sqlalchemy.orm import Session
from openpyxl import load_workbook

from app.core.logger import logger
from app.models.product import Product


UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def save_file(file: UploadFile):

    logger.info(f"Uploading file: {file.filename}")

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    try:

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        logger.info(
            f"File uploaded successfully: {file.filename}"
        )

        return file_path


    except Exception as e:

        logger.error(
            f"File upload failed: {str(e)}"
        )

        raise



def import_products_from_excel(
    file_path: str,
    db: Session
):

    workbook = load_workbook(
        file_path
    )

    sheet = workbook.active


    products = []


    # Skip header row
    for row in sheet.iter_rows(
        min_row=2,
        values_only=True
    ):

        name, sku, quantity, price = row[:4]


        product = Product(
            name=name,
            sku=sku,
            quantity=quantity,
            price=price
        )


        products.append(product)


    db.add_all(products)

    db.commit()


    return len(products)