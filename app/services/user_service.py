from sqlalchemy.orm import Session
from app.models.user import User
from app.core.logger import logger


# GET ALL USERS
def get_all_users(db: Session):
    logger.info("Fetching all users")

    users = db.query(User).all()

    logger.info(f"Total users found: {len(users)}")

    return users


# GET USER BY ID
def get_user_by_id(db: Session, user_id: int):
    logger.info(f"Fetching user by ID: {user_id}")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        logger.warning(f"User not found: ID {user_id}")
        return None

    logger.info(f"User found: {user.email}")

    return user


# UPDATE USER ROLE
def update_user_role(db: Session, user_id: int, role: str):
    logger.info(f"Updating role for user ID: {user_id} to {role}")

    user = get_user_by_id(db, user_id)

    if not user:
        logger.warning(f"Role update failed - user not found: {user_id}")
        return None

    old_role = user.role
    user.role = role

    db.commit()
    db.refresh(user)

    logger.info(
        f"User role updated successfully: ID {user_id}, {old_role} → {role}"
    )

    return user


# DISABLE USER
def disable_user(db: Session, user_id: int):
    logger.info(f"Disabling user ID: {user_id}")

    user = get_user_by_id(db, user_id)

    if not user:
        logger.warning(f"Disable failed - user not found: {user_id}")
        return None

    user.is_active = False

    db.commit()
    db.refresh(user)

    logger.info(f"User disabled successfully: ID {user_id}")

    return user