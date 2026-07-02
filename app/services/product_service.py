from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.core.logger import logger


# CREATE PRODUCT
def create_product(db: Session, product: ProductCreate):
    logger.info(f"Creating product: {product.name}, SKU: {product.sku}")

    db_product = Product(
        name=product.name,
        sku=product.sku,
        quantity=product.quantity,
        price=product.price
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    logger.info(f"Product created successfully with ID: {db_product.id}")

    return db_product


# GET ALL PRODUCTS
def get_all_products(db):
    logger.info("Fetching all products")

    products = db.query(Product).all()

    logger.info(f"Total products found: {len(products)}")

    return products


# GET BY ID
def get_product_by_id(db, product_id: int):
    logger.info(f"Fetching product by ID: {product_id}")

    product = db.query(Product).filter(Product.id == product_id).first()

    if product:
        logger.info(f"Product found: {product.name}")
    else:
        logger.warning(f"Product not found: ID {product_id}")

    return product


# UPDATE PRODUCT
def update_product(db, product_id: int, product: ProductUpdate):
    logger.info(f"Updating product ID: {product_id}")

    db_product = db.query(Product).filter(Product.id == product_id).first()

    if not db_product:
        logger.warning(f"Update failed - Product not found: {product_id}")
        return None

    db_product.name = product.name
    db_product.sku = product.sku
    db_product.quantity = product.quantity
    db_product.price = product.price

    db.commit()
    db.refresh(db_product)

    logger.info(f"Product updated successfully: ID {product_id}")

    return db_product


# DELETE PRODUCT
def delete_product(db, product_id: int):
    logger.info(f"Deleting product ID: {product_id}")

    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        logger.warning(f"Delete failed - Product not found: {product_id}")
        return None

    db.delete(product)
    db.commit()

    logger.info(f"Product deleted successfully: ID {product_id}")

    return product