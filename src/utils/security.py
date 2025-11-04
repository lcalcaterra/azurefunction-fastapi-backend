import os, jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import Request, HTTPException

SECRET_KEY = os.getenv("JWT_SECRET", "")

def verify_user(request: Request):
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")