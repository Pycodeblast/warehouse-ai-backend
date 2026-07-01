from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

def create_product(db: Session, product: ProductCreate):
    db_product = Product(
        name=product.name,
        sku=product.sku,
        quantity=product.quantity,
        price=product.price
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product

def get_all_products(db):
    return db.query(Product).all()

def get_product_by_id(db, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

def update_product(db, product_id: int, product: ProductUpdate):
    db_product = db.query(Product).filter(Product.id == product_id).first()

    if not db_product:
        return None

    db_product.name = product.name
    db_product.sku = product.sku
    db_product.quantity = product.quantity
    db_product.price = product.price

    db.commit()
    db.refresh(db_product)

    return db_product

def delete_product(db, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        return None

    db.delete(product)
    db.commit()

    return product

