import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from pydantic import BaseModel
from types import SimpleNamespace
from ..database import banco_dados
from ..database.modelos import Empresa
from ..schemas.empresa import EmpresaCreate, EmpresaOut, hash_password, verify_password
from ..utils.timezone_utils import agora_sp
from ..utils.token_utils import create_confirmation_token, verify_confirmation_token
from ..utils.email_utils import  enviar_email_recuperacao
from datetime import datetime, timedelta, timezone

router = APIRouter(tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

ADMIN_EMAIL = "admin@rmtpark.com"
ADMIN_PASSWORD = "admin@123"
ADMIN_NAME = "Administrador Master"

def criar_token(dados: dict):
    to_encode = dados.copy()
    expira = agora_sp() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expira})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_empresa(
    db: Session = Depends(banco_dados.get_db),
    token: str = Depends(oauth2_scheme)
) -> SimpleNamespace:
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

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_admin: bool = False

def create_tokens(email: str):
    now = datetime.now(timezone.utc)
    access_token = jwt.encode(
        {"sub": email, "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    refresh_token = jwt.encode(
        {"sub": email, "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "type": "refresh"},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return access_token, refresh_token


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(banco_dados.get_db)):
    if form_data.username == ADMIN_EMAIL and form_data.password == ADMIN_PASSWORD:
        access_token, refresh_token = create_tokens(ADMIN_EMAIL)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "is_admin": True}

    empresa = db.query(Empresa).filter(Empresa.email == form_data.username).first()
    if not empresa or not verify_password(form_data.password, empresa.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not empresa.email_confirmado:
        raise HTTPException(status_code=403, detail="E-mail não confirmado. Confirme seu e-mail antes de fazer login.")

    access_token, refresh_token = create_tokens(empresa.email)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "is_admin": False}

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh-token", response_model=TokenResponse)
def refresh_token(data: RefreshTokenRequest):
    try:
        payload = jwt.decode(data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Token inválido")
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    access_token, refresh_token = create_tokens(email)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "is_admin": email == ADMIN_EMAIL}

@router.get("/confirmar-email")
def confirmar_email(token: str, db: Session = Depends(banco_dados.get_db)):
    email = verify_confirmation_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    empresa = db.query(Empresa).filter(Empresa.email == email).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    empresa.email_confirmado = True
    db.commit()
    return {"msg": "E-mail confirmado com sucesso! Agora você pode fazer login."}

class RecuperarSenhaRequest(BaseModel):
    email: str

@router.post("/recuperar-senha")
async def recuperar_senha(dados: RecuperarSenhaRequest, db: Session = Depends(banco_dados.get_db)):
    empresa = db.query(Empresa).filter(Empresa.email == dados.email).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="E-mail não encontrado")

    token = create_confirmation_token(dados.email)
    await enviar_email_recuperacao(dados.email, token)
    return {"msg": "Link de recuperação enviado para seu e-mail"}

class RedefinirSenhaRequest(BaseModel):
    token: str
    nova_senha: str

@router.post("/redefinir-senha")
def redefinir_senha(dados: RedefinirSenhaRequest, db: Session = Depends(banco_dados.get_db)):
    email = verify_confirmation_token(dados.token)
    if not email:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    empresa = db.query(Empresa).filter(Empresa.email == email).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    empresa.senha = hash_password(dados.nova_senha)
    db.commit()
    return {"msg": "Senha redefinida com sucesso"}
