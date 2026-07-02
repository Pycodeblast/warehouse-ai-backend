from sqlalchemy.orm import Session
from app.models.product import Product
from app.core.logger import logger


# GET INVENTORY
def get_inventory(db: Session):
    logger.info("Fetching inventory (all products)")

    products = db.query(Product).all()

    logger.info(f"Inventory fetched successfully. Total items: {len(products)}")

    return products


# STOCK IN
def stock_in(db: Session, product_id: int, quantity: int):
    logger.info(f"Stock IN request - Product ID: {product_id}, Quantity: {quantity}")

    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        logger.warning(f"Stock IN failed - Product not found: ID {product_id}")
        return None

    product.quantity += quantity
    db.commit()
    db.refresh(product)

    logger.info(
        f"Stock IN successful - Product ID: {product_id}, New Quantity: {product.quantity}"
    )

    return product


# STOCK OUT
def stock_out(db: Session, product_id: int, quantity: int):
    logger.info(f"Stock OUT request - Product ID: {product_id}, Quantity: {quantity}")

    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        logger.warning(f"Stock OUT failed - Product not found: ID {product_id}")
        return None

    if product.quantity < quantity:
        logger.warning(
            f"Stock OUT failed - Insufficient stock for Product ID: {product_id}, Available: {product.quantity}"
        )
        return "insufficient"

    product.quantity -= quantity
    db.commit()
    db.refresh(product)

    logger.info(
        f"Stock OUT successful - Product ID: {product_id}, New Quantity: {product.quantity}"
    )

    return product