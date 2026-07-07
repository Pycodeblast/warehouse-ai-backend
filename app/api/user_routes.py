from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.rbac import require_role

from app.services.user_service import (
    get_all_users,
    update_user_role,
    disable_user,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/")
def list_users(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    require_role(user, ["admin"])
    return get_all_users(db)


@router.put("/{user_id}/role")
def change_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    require_role(user, ["admin"])

    updated_user = update_user_role(db, user_id, role)

    if not updated_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return updated_user


@router.put("/{user_id}/disable")
def disable_existing_user(
    user_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    require_role(user, ["admin"])

    disabled_user = disable_user(db, user_id)

    if not disabled_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "message": "User disabled successfully"
    }