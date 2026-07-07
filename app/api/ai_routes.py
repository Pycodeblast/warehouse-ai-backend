from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.dependencies import get_current_user
from app.auth.rbac import require_role

from app.services.ai_service import (
    ask_ai,
    get_chat_history,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


class AIRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_question(
    request: AIRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    require_role(user, ["admin", "manager", "viewer"])

    return ask_ai(
        db=db,
        question=request.question,
        current_user=user,
    )

@router.get("/history")
def chat_history(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    require_role(
        user,
        ["admin", "manager", "viewer"],
    )

    return get_chat_history(
        db=db,
        current_user=user,
    )