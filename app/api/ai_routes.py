from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.dependencies import get_current_user
from app.auth.rbac import require_role

from app.services.ai_service import ask_ai
from app.services.ai_chat_service import get_chat_history
from app.services.activity_service import create_activity

from app.models.user import User

router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


class AIRequest(BaseModel):
    question: str


# ---------------------------------
# ASK AI
# ---------------------------------

@router.post("/ask")
def ask_question(
    request: AIRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    require_role(
        user,
        ["admin", "manager", "viewer"]
    )

    response = ask_ai(
        db,
        user["user_id"],
        request.question
    )

    logged_user = (
        db.query(User)
        .filter(User.id == user["user_id"])
        .first()
    )

    if logged_user:
        create_activity(
            db=db,
            module="AI",
            action="Question",
            description=request.question,
            username=logged_user.username
        )

    return response


# ---------------------------------
# CHAT HISTORY
# ---------------------------------

@router.get("/history")
def chat_history(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    require_role(
        user,
        ["admin", "manager", "viewer"]
    )

    return get_chat_history(
        db,
        user["user_id"]
    )