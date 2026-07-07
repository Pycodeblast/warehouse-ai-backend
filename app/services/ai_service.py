import requests

from sqlalchemy.orm import Session

from app.models.product import Product
from app.core.logger import logger
from app.services.ai_chat_service import save_chat


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "phi3"



# ---------------------------------
# Get Inventory Data From Database
# ---------------------------------

def get_inventory_context(db: Session):

    products = (
        db.query(Product)
        .all()
    )


    if not products:
        return "No products available in inventory."


    total_products = len(products)


    total_quantity = sum(
        product.quantity
        for product in products
    )


    product_details = "\n".join(
        [
            f"""
Product Name: {product.name}
SKU: {product.sku}
Quantity: {product.quantity}
Price: {product.price}
"""
            for product in products
        ]
    )


    context = f"""

Warehouse Inventory Summary

Total Product Types:
{total_products}


Total Available Quantity:
{total_quantity}


Product Details:

{product_details}

"""


    return context





# ---------------------------------
# Ask AI
# ---------------------------------

def ask_ai(
    db: Session,
    user_id: int,
    question: str
):

    logger.info(
        f"AI request received: {question}"
    )


    try:

        inventory_context = get_inventory_context(db)



        prompt = f"""

You are a warehouse management assistant.

You have access to the warehouse inventory data below.

Use only this data to answer user questions.

If the answer is not available in the data,
say that information is not available.


Inventory Data:

{inventory_context}



User Question:

{question}



Give a short and clear answer.

"""



        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )



        result = response.json()



        answer = result.get(
            "response",
            "No response generated"
        )



        logger.info(
            "AI response generated successfully"
        )
        save_chat(
    db=db,
    user_id=user_id,
    question=question,
    answer=answer.strip()
)



        return {

            "question": question,

            "answer": answer.strip()

        }



    except Exception as e:

        logger.error(
            f"Ollama AI failed: {str(e)}"
        )


        return {

            "question": question,

            "answer": "AI service unavailable"

        }