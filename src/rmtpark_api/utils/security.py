from types import SimpleNamespace
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from ..database.modelos import Empresa
from ..database import banco_dados
import os

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
ADMIN_NAME = os.getenv("ADMIN_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")

def get_current_empresa(db: Session = Depends(banco_dados.get_db), token: str = Depends(oauth2_scheme)):
    """
    Aceita tanto o token JWT quanto um token simples 'admin-local-token' para admin.
    """
    # Token local fixo
    if token == "admin-local-token":
        return SimpleNamespace(email=ADMIN_EMAIL, nome=ADMIN_NAME, is_admin=True)

    # JWT normal
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    if email == ADMIN_EMAIL:
        return SimpleNamespace(email=ADMIN_EMAIL, nome=ADMIN_NAME, is_admin=True)

    empresa = db.query(Empresa).filter(Empresa.email == email).first()
    if not empresa:
        raise HTTPException(status_code=401, detail="Empresa não encontrada")

    setattr(empresa, "is_admin", False)
    return empresa

# ---------------- Função require_admin ----------------
def require_admin(empresa=Depends(get_current_empresa)):
    """
    Garante que apenas admin possa acessar a rota.
    """
    if not getattr(empresa, "is_admin", False):
        raise HTTPException(status_code=403, detail="Acesso restrito ao admin")
    return empresa