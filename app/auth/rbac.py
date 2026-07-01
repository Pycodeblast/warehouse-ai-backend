from fastapi import HTTPException

def require_role(user, allowed_roles: list):
    if user["role"] not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this resource"
        )