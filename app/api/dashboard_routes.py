from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.dependencies import get_current_user
from app.services.dashboard_service import get_dashboard_stats
from app.services.activity_service import get_recent_activities

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return get_dashboard_stats(db)


# ----------------------------------
# RECENT ACTIVITY (LAST 10 / 24 HOURS)
# ----------------------------------
@router.get("/activity")
def dashboard_activity(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    activities = get_recent_activities(db, limit=10)

    return [
        {
            "module": a.module,
            "action": a.action,
            "description": a.description,
            "username": a.username,
            "time": a.created_at,
        }
        for a in activities
    ]