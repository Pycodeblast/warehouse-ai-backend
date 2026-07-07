import os

from datetime import datetime, time

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.user import User
from app.models.ai_chat import AIChat



# -----------------------------------
# GET DASHBOARD STATS
# -----------------------------------

def get_dashboard_stats(db: Session):

    # -----------------------------
    # TOTAL PRODUCTS
    # -----------------------------

    total_products = (
        db.query(Product)
        .count()
    )


    # -----------------------------
    # TOTAL USERS
    # -----------------------------

    total_users = (
        db.query(User)
        .count()
    )


    # -----------------------------
    # TOTAL UPLOADED FILES
    # -----------------------------

    total_files = (
        len(os.listdir("uploads"))
        if os.path.exists("uploads")
        else 0
    )


    # -----------------------------
    # TODAY AI REQUEST COUNT
    # -----------------------------

    today_start = datetime.combine(
        datetime.now().date(),
        time.min
    )


    today_ai_requests = (
        db.query(AIChat)
        .filter(
            AIChat.created_at >= today_start
        )
        .count()
    )


    # -----------------------------
    # RESPONSE
    # -----------------------------

    return {

        "totalProducts": total_products,

        "totalInventory": total_products,

        "totalUsers": total_users,

        "totalFiles": total_files,

        "todayAiRequests": today_ai_requests,

    }

    