from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("user_id")
        role = payload.get("role")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {"user_id": user_id, "role": role}

    except JWTError:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")