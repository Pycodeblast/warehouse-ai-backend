import requests

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.user import User
from app.core.logger import logger
from app.services.ai_chat_service import save_chat

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3"


# ------------------------------------------------
# Inventory Context
# ------------------------------------------------

def get_inventory_context(db: Session):

    products = db.query(Product).limit(20).all()

    if not products:
        return "No products available in inventory."

    total_products = len(products)

    total_quantity = sum(
        product.quantity
        for product in products
    )

    product_details = "\n".join(
        [
            f"- {product.name} | SKU: {product.sku} | Quantity: {product.quantity} | Price: ₹{product.price}"
            for product in products
        ]
    )

    return f"""
Warehouse Inventory Summary

Total Product Types:
{total_products}

Total Available Quantity:
{total_quantity}

Product Details:

{product_details}
"""


# ------------------------------------------------
# Ask AI
# ------------------------------------------------

def ask_ai(
    db: Session,
    user_id: int,
    question: str,
):

    logger.info(f"AI request received: {question}")

    question_lower = question.lower().strip()

    # ----------------------------------------
    # Quick Database Answers
    # ----------------------------------------

    if (
        "how many products" in question_lower
        or "product count" in question_lower
        or "total products" in question_lower
    ):

        answer = str(db.query(Product).count())

        save_chat(
            db=db,
            user_id=user_id,
            question=question,
            answer=answer,
        )

        return {
            "question": question,
            "answer": answer,
        }

    if (
        "how many users" in question_lower
        or "user count" in question_lower
        or "total users" in question_lower
    ):

        answer = str(db.query(User).count())

        save_chat(
            db=db,
            user_id=user_id,
            question=question,
            answer=answer,
        )

        return {
            "question": question,
            "answer": answer,
        }

    if "active users" in question_lower:

        answer = str(
            db.query(User)
            .filter(User.is_active == True)
            .count()
        )

        save_chat(
            db=db,
            user_id=user_id,
            question=question,
            answer=answer,
        )

        return {
            "question": question,
            "answer": answer,
        }

    if (
        "inactive users" in question_lower
        or "disabled users" in question_lower
    ):

        answer = str(
            db.query(User)
            .filter(User.is_active == False)
            .count()
        )

        save_chat(
            db=db,
            user_id=user_id,
            question=question,
            answer=answer,
        )

        return {
            "question": question,
            "answer": answer,
        }

    if (
        "low stock" in question_lower
        or "less stock" in question_lower
    ):

        products = (
            db.query(Product)
            .filter(Product.quantity < 10)
            .all()
        )

        if products:

            answer = "\n".join(
                [
                    f"{p.name} (Qty: {p.quantity})"
                    for p in products
                ]
            )

        else:

            answer = "No low stock products found."

        save_chat(
            db=db,
            user_id=user_id,
            question=question,
            answer=answer,
        )

        return {
            "question": question,
            "answer": answer,
        }

    if "out of stock" in question_lower:

        products = (
            db.query(Product)
            .filter(Product.quantity == 0)
            .all()
        )

        if products:

            answer = "\n".join(
                [
                    p.name
                    for p in products
                ]
            )

        else:

            answer = "No out of stock products."

        save_chat(
            db=db,
            user_id=user_id,
            question=question,
            answer=answer,
        )

        return {
            "question": question,
            "answer": answer,
        }

    # ----------------------------------------
    # AI Answer
    # ----------------------------------------

    try:

        inventory_context = get_inventory_context(db)

        prompt = f"""
You are WarehouseAI, an AI assistant for a Warehouse Inventory Management System.

You answer ONLY warehouse and inventory related questions.

Inventory Data:

{inventory_context}

Rules:

1. Use ONLY the inventory data above.
2. Never invent products, users, quantities or prices.
3. If information is unavailable, reply:
"I don't have enough information to answer that."
4. Keep answers short and professional.
5. If asked to summarize inventory, provide a concise summary.
6. If asked for stock, mention product name and quantity.
7. If asked for prices, use the stored prices.
8. If asked for recommendations (restocking, inventory management, etc.), provide practical advice based on the inventory data.
9. If the question is unrelated to warehouse management, reply:
"I'm designed to answer questions about this Warehouse Management System only."

Question:
{question}

Answer:
"""

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=300,
        )

        result = response.json()

        answer = result.get(
            "response",
            "No response generated"
        ).strip()

        save_chat(
            db=db,
            user_id=user_id,
            question=question,
            answer=answer,
        )

        logger.info("AI response generated successfully")

        return {
            "question": question,
            "answer": answer,
        }

    except Exception as e:

        logger.error(f"Ollama AI failed: {e}")

        return {
            "question": question,
            "answer": "AI service unavailable",
        }