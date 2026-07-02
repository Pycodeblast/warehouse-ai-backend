from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.auth.rbac import require_role

from app.database.database import get_db
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate
)
from app.services.product_service import (
    create_product,
    get_all_products,
    get_product_by_id,
    update_product, delete_product
)

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.post("/", response_model=ProductResponse)
def create_new_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    require_role(user, ["admin", "manager"])

    return create_product(db, product)

@router.get("/", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return get_all_products(db)

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product

@router.put("/{product_id}", response_model=ProductResponse)
def update_existing_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    require_role(user, ["admin", "manager"])

    updated_product = update_product(db, product_id, product)

    if not updated_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return updated_product

@router.delete("/{product_id}")
def delete_existing_product(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    require_role(user, ["admin"])

    deleted_product = delete_product(db, product_id)

    if not deleted_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return {
        "message": "Product deleted successfully"
    }

