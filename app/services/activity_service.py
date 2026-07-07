from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.activity_log import ActivityLog


def create_activity(db: Session, module: str, action: str, description: str, username: str):
    activity = ActivityLog(
        module=module,
        action=action,
        description=description,
        username=username,
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    return activity


def get_recent_activities(db: Session, limit: int = 10):

    # last 24 hours filter
    time_limit = datetime.utcnow() - timedelta(hours=24)

    return (
        db.query(ActivityLog)
        .filter(ActivityLog.created_at >= time_limit)
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
        .all()
    )