import os
import datetime
import jwt
from fastapi import APIRouter, Request, HTTPException, status

from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


SECRET_KEY = os.getenv("JWT_SECRET", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 15


def create_access_token(subject: str):
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ---- helper: verify token from Authorization header ----
def verify_user_from_header(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

