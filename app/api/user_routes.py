from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.dependencies import get_current_user
from app.auth.rbac import require_role

from app.schemas.user import UserCreateByAdmin

from app.services.user_service import (
    get_all_users,
    create_user,
    update_user_role,
    disable_user,
     enable_user,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ----------------------------------
# LIST USERS
# ----------------------------------
@router.get("/")
def list_users(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_role(current_user, ["admin", "manager"])

    return get_all_users(db)


# ----------------------------------
# CREATE USER (ADMIN)
# ----------------------------------
@router.post("/create")
def create_new_user(
    user_data: UserCreateByAdmin,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_role(current_user, ["admin"])

    new_user = create_user(
        db,
        user_data,
        current_user,
    )

    if not new_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )

    return {
        "message": "User created successfully",
        "user": new_user,
    }


# ----------------------------------
# UPDATE USER ROLE
# ----------------------------------
@router.put("/{user_id}/role")
def change_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_role(current_user, ["admin"])

    updated_user = update_user_role(
        db,
        user_id,
        role,
        current_user,
    )

    if not updated_user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return {
        "message": "Role updated successfully",
        "user": updated_user,
    }


# ----------------------------------
# DISABLE USER
# ----------------------------------
@router.put("/{user_id}/disable")
def disable_existing_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_role(current_user, ["admin"])

    disabled_user = disable_user(
        db,
        user_id,
        current_user,
    )

    if not disabled_user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return {
        "message": "User disabled successfully"
    }

@router.put("/{user_id}/enable")
def enable_existing_user(
    user_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    require_role(user, ["admin"])

    enabled_user = enable_user(db, user_id)

    if not enabled_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "message": "User enabled successfully"
    }