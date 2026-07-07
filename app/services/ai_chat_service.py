from sqlalchemy.orm import Session

from app.models.ai_chat import AIChat


def save_chat(
    db: Session,
    user_id: int,
    question: str,
    answer: str,
):
    chat = AIChat(
        user_id=user_id,
        question=question,
        answer=answer,
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat


def get_chat_history(
    db: Session,
    user_id: int,
):
    return (
        db.query(AIChat)
        .filter(AIChat.user_id == user_id)
        .order_by(AIChat.created_at.asc())
        .all()
    )