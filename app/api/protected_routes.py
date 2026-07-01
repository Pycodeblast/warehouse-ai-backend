from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user
from app.auth.rbac import require_role

router = APIRouter()


@router.get("/profile")
def get_profile(user=Depends(get_current_user)):
    return {
        "message": "This is protected route",
        "user": user
    }

# Admin only route
@router.get("/admin")
def admin_panel(user=Depends(get_current_user)):
    require_role(user, ["admin"])

    return {
        "message": "Welcome Admin"
    }


# Admin + Manager
@router.get("/dashboard")
def dashboard(user=Depends(get_current_user)):
    require_role(user, ["admin", "manager"])

    return {
        "message": "Dashboard data"
    }