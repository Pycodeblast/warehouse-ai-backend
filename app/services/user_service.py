from sqlalchemy.orm import Session
from app.models.user import User
from app.core.logger import logger


# -----------------------------
# CLEAN SERIALIZER (IMPORTANT)
# -----------------------------
def serialize_user(user: User):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at
    }


# -----------------------------
# GET ALL USERS
# -----------------------------
def get_all_users(db: Session):
    logger.info("Fetching all users")

    users = db.query(User).all()

    logger.info(f"Total users found: {len(users)}")

    return [serialize_user(user) for user in users]


# -----------------------------
# GET USER BY ID
# -----------------------------
def get_user_by_id(db: Session, user_id: int):
    logger.info(f"Fetching user by ID: {user_id}")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        logger.warning(f"User not found: ID {user_id}")
        return None

    logger.info(f"User found: {user.email}")

    return serialize_user(user)


# -----------------------------
# UPDATE USER ROLE
# -----------------------------
def update_user_role(db: Session, user_id: int, role: str):
    logger.info(f"Updating role for user ID: {user_id} → {role}")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        logger.warning(f"Role update failed - user not found: {user_id}")
        return None

    old_role = user.role
    user.role = role

    db.commit()
    db.refresh(user)

    logger.info(f"Role updated: {old_role} → {role} for user {user_id}")

    return {
        "id": user.id,
        "role": user.role
    }


# -----------------------------
# DISABLE USER
# -----------------------------
def disable_user(db: Session, user_id: int):
    logger.info(f"Disabling user ID: {user_id}")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        logger.warning(f"Disable failed - user not found: {user_id}")
        return None

    user.is_active = False

    db.commit()
    db.refresh(user)

    logger.info(f"User disabled successfully: ID {user_id}")

    return {
        "id": user.id,
        "is_active": user.is_active
    }

# -----------------------------
# ENABLE USER
# -----------------------------
def enable_user(db: Session, user_id: int):
    logger.info(f"Enabling user ID: {user_id}")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        logger.warning(f"Enable failed - user not found: {user_id}")
        return None

    user.is_active = True

    db.commit()
    db.refresh(user)

    logger.info(f"User enabled successfully: ID {user_id}")

    return {
        "id": user.id,
        "is_active": user.is_active
    }