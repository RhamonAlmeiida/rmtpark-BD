from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import os

from ..database.banco_dados import get_db
from ..database.modelos import Empresa

# -----------------------------
# Configurações do JWT
# -----------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")  # Recomenda usar .env
ALGORITHM = "HS256"

# OAuth2 para receber token via Header: Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_empresa(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> Empresa:
    """
    Retorna a empresa autenticada com base no token JWT.
    """
    try:
        # decodifica o token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    # busca empresa no banco
    empresa = db.query(Empresa).filter(Empresa.email == email).first()
    if not empresa:
        raise HTTPException(status_code=401, detail="Empresa não encontrada")

    return empresa
