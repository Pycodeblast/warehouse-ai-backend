import requests
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.user import User
from app.models.ai_chat import AIChat

from app.core.logger import logger
from app.services.ai_chat_service import save_chat

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3"


def ask_ai(db: Session, question: str,  current_user):
    logger.info(f"AI request received: {question}")

    question_lower = question.lower().strip()

    # ------------------------------------------------
    # PRODUCT COUNT
    # ------------------------------------------------
    if (
        "how many products" in question_lower
        or "product count" in question_lower
        or "total products" in question_lower
    ):
        count = db.query(Product).count()

        save_chat(
    db=db,
    user_id=current_user["user_id"],
    question=question,
    answer=str(count),
)

        return {
            "question": question,
            "answer": str(count),
        }

    # ------------------------------------------------
    # USER COUNT
    # ------------------------------------------------
    if (
        "how many users" in question_lower
        or "user count" in question_lower
        or "total users" in question_lower
    ):
        count = db.query(User).count()

        return {
            "question": question,
            "answer": str(count),
        }

    # ------------------------------------------------
    # ACTIVE USERS
    # ------------------------------------------------
    if "active users" in question_lower:
        count = (
            db.query(User)
            .filter(User.is_active == True)
            .count()
        )

        return {
            "question": question,
            "answer": str(count),
        }

    # ------------------------------------------------
    # DISABLED USERS
    # ------------------------------------------------
    if (
        "disabled users" in question_lower
        or "inactive users" in question_lower
    ):
        count = (
            db.query(User)
            .filter(User.is_active == False)
            .count()
        )

        return {
            "question": question,
            "answer": str(count),
        }

    # ------------------------------------------------
    # LOW STOCK PRODUCTS
    # ------------------------------------------------
    if (
        "low stock" in question_lower
        or "less stock" in question_lower
    ):
        products = (
            db.query(Product)
            .filter(Product.quantity < 10)
            .all()
        )

        if not products:
            return {
                "question": question,
                "answer": "No low stock products found.",
            }

        answer = "\n".join(
            [
                f"{p.name} (Qty: {p.quantity})"
                for p in products
            ]
        )

        return {
            "question": question,
            "answer": answer,
        }

    # ------------------------------------------------
    # OUT OF STOCK
    # ------------------------------------------------
    if "out of stock" in question_lower:

        products = (
            db.query(Product)
            .filter(Product.quantity == 0)
            .all()
        )

        if not products:
            return {
                "question": question,
                "answer": "No out of stock products.",
            }

        answer = "\n".join(
            [
                p.name
                for p in products
            ]
        )

        return {
            "question": question,
            "answer": answer,
        }

    # ------------------------------------------------
    # FETCH DATA
    # ------------------------------------------------
    products = db.query(Product).all()
    users = db.query(User).all()

    # ------------------------------------------------
    # BUILD PRODUCT CONTEXT
    # ------------------------------------------------
    product_context = ""

    if products:

        for product in products[:30]:

            product_context += (
                f"- {product.name} | "
                f"SKU: {product.sku} | "
                f"Qty: {product.quantity} | "
                f"Price: ₹{product.price}\n"
            )

    else:

        product_context = "No products available.\n"

    # ------------------------------------------------
    # BUILD USER CONTEXT
    # ------------------------------------------------
    user_context = ""

    if users:

        for user in users:

            status = (
                "Active"
                if user.is_active
                else "Disabled"
            )

            user_context += (
                f"- {user.username} | "
                f"{user.role} | "
                f"{status}\n"
            )

    else:

        user_context = "No users available.\n"

    # ------------------------------------------------
    # AI PROMPT
    # ------------------------------------------------
    prompt = f"""
You are an AI Assistant for a Warehouse Management System.

You MUST answer ONLY using the information below.

Products:
{product_context}

Users:
{user_context}

Rules:

1. Never invent information.

2. Never guess.

3. Never repeat products.

4. Keep answers short.

5. If asked for quantity, use Qty.

6. If asked for price, use Price.

7. If asked to list products, return matching products only.

8. If asked something unavailable, reply:
"I don't have enough data to answer that."

Maximum response length: 100 words.

Question:

{question}

Answer:
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0,
                    "top_p": 0.9,
                    "num_predict": 200,
                },
            },
            timeout=60,
        )

        response.raise_for_status()

        result = response.json()

        answer = result.get(
            "response",
            "No response from AI",
        ).strip()
        save_chat(
    db=db,
    user_id=current_user["user_id"],
    question=question,
    answer=answer,
)

        logger.info("AI response generated successfully")

        return {
            "question": question,
            "answer": answer,
        }

    except Exception as e:

        logger.error(f"Ollama AI failed: {str(e)}")

        return {
            "question": question,
            "answer": "AI service unavailable.",
        }

# ------------------------------------------------
# GET CHAT HISTORY
# ------------------------------------------------
def get_chat_history(
    db: Session,
    current_user,
):

    chats = (
        db.query(AIChat)
        .filter(
            AIChat.user_id == current_user["user_id"]
        )
        .order_by(
            AIChat.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": chat.id,
            "question": chat.question,
            "answer": chat.answer,
            "created_at": chat.created_at,
        }
        for chat in chats
    ]