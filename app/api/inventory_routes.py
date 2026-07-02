from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.rbac import require_role

from app.services.inventory_service import (
    get_inventory,
    stock_in,
    stock_out,
)

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)


@router.get("/")
def list_inventory(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    require_role(user, ["admin", "manager", "viewer"])
    return get_inventory(db)


@router.post("/stock-in/{product_id}")
def add_stock(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    require_role(user, ["admin", "manager"])

    product = stock_in(db, product_id, quantity)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


@router.post("/stock-out/{product_id}")
def remove_stock(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    require_role(user, ["admin", "manager"])

    product = stock_out(db, product_id, quantity)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if product == "insufficient":
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock"
        )

    return product