from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.auth.rbac import require_role
from app.services.ai_service import ask_ai


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


class AIRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_question(
    request: AIRequest,
    user=Depends(get_current_user)
):
    require_role(user, ["admin", "manager", "viewer"])

    return ask_ai(request.question)