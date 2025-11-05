from datetime import datetime, timedelta
from jose import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_tokens(email: str):
    now = datetime.now()
    access_token = jwt.encode({"sub": email, "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}, SECRET_KEY, algorithm=ALGORITHM)
    refresh_token = jwt.encode({"sub": email, "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "type": "refresh"}, SECRET_KEY, algorithm=ALGORITHM)
    return access_token, refresh_token

def create_confirmation_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def verify_confirmation_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except:
        return None
