from sqlalchemy.orm import Session

from app.models.user import User
from app.auth.auth import hash_password
from app.core.logger import logger

from app.services.activity_service import create_activity


# -----------------------------
# SERIALIZER
# -----------------------------
def serialize_user(user: User):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


# -----------------------------
# CREATE USER (ADMIN)
# -----------------------------
def create_user(db: Session, user_data, current_user):
    logger.info(f"Creating user: {user_data.email}")

    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        logger.warning(f"User already exists: {user_data.email}")
        return None

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    admin = (
        db.query(User)
        .filter(User.id == current_user["user_id"])
        .first()
    )

    create_activity(
        db=db,
        module="User",
        action="CREATE",
        description=f"{admin.username} created user {new_user.username}",
        username=admin.username,
    )

    logger.info(f"User created successfully: {new_user.email}")

    return serialize_user(new_user)


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

    return serialize_user(user)


# -----------------------------
# UPDATE USER ROLE
# -----------------------------
def update_user_role(db: Session, user_id: int, role: str, current_user):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return None

    old_role = user.role
    user.role = role

    db.commit()
    db.refresh(user)

    admin = (
        db.query(User)
        .filter(User.id == current_user["user_id"])
        .first()
    )

    create_activity(
        db=db,
        module="User",
        action="UPDATE_ROLE",
        description=f"{admin.username} changed role of {user.username} from {old_role} to {role}",
        username=admin.username,
    )

    return serialize_user(user)


# -----------------------------
# DISABLE USER
# -----------------------------
def disable_user(db: Session, user_id: int, current_user):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return None

    user.is_active = False

    db.commit()
    db.refresh(user)

    admin = (
        db.query(User)
        .filter(User.id == current_user["user_id"])
        .first()
    )

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
    