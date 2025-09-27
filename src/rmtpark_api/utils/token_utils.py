# tokens.py
from datetime import datetime, timedelta
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24h
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_confirmation_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": int(expire.timestamp())}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_confirmation_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

def create_tokens(email: str):
    now = datetime.utcnow()
    access_token_expires = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = jwt.encode(
        {"sub": email, "exp": int(access_token_expires.timestamp())},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    refresh_token = jwt.encode(
        {"sub": email, "exp": int(refresh_token_expires.timestamp()), "type": "refresh"},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return access_token, refresh_token
