# src/rmtpark_api/api/auth.py
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from pydantic import BaseModel

from ..database import banco_dados
from ..database.modelos import Empresa
from ..schemas.empresa import EmpresaCreate, EmpresaOut, hash_password, verify_password
from ..utils.token_utils import create_confirmation_token, verify_confirmation_token
from ..utils.email_utils import enviar_email_confirmacao, enviar_email_recuperacao

router = APIRouter(prefix="/auth", tags=["auth"])

# ==========================================
# CONFIGURAÇÃO DE JWT
# ==========================================
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

FRONT_URL = os.getenv("FRONT_URL", "http://localhost:4200")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ==========================================
# FUNÇÃO PARA PEGAR EMPRESA AUTENTICADA
# ==========================================
def get_current_empresa(
    db: Session = Depends(banco_dados.get_db),
    token: str = Depends(oauth2_scheme)
) -> Empresa:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    empresa = db.query(Empresa).filter(Empresa.email == email).first()
    if not empresa:
        raise HTTPException(status_code=401, detail="Empresa não encontrada")

    return empresa

# ==========================================
# CADASTRAR EMPRESA
# ==========================================
@router.post("/cadastrar", response_model=EmpresaOut)
async def cadastrar(empresa: EmpresaCreate, db: Session = Depends(banco_dados.get_db)):
    if db.query(Empresa).filter(Empresa.email == empresa.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    hashed_senha = hash_password(empresa.senha)
    nova_empresa = Empresa(
        nome=empresa.nome,
        email=empresa.email,
        telefone=empresa.telefone,
        cnpj=empresa.cnpj,
        senha=hashed_senha,
        email_confirmado=False,
    )

    db.add(nova_empresa)
    db.commit()
    db.refresh(nova_empresa)

    # envia email de confirmação com FRONT_URL
    token = create_confirmation_token(nova_empresa.email)
    link = f"{FRONT_URL}/confirmar-email?token={token}"
    await enviar_email_confirmacao(nova_empresa.email, link)

    return nova_empresa

# ==========================================
# CONFIRMAR EMAIL
# ==========================================
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

    return {"msg": "E-mail confirmado com sucesso! Pode fazer login."}

# ==========================================
# LOGIN COM ACCESS E REFRESH TOKENS
# ==========================================
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

def create_tokens(email: str):
    now = datetime.utcnow()

    access_token_expires = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {"sub": email, "exp": access_token_expires}, SECRET_KEY, algorithm=ALGORITHM
    )

    refresh_token_expires = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = jwt.encode(
        {"sub": email, "exp": refresh_token_expires, "type": "refresh"},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return access_token, refresh_token

@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(banco_dados.get_db)):
    empresa = db.query(Empresa).filter(Empresa.email == form_data.username).first()
    if not empresa or not verify_password(form_data.password, empresa.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not empresa.email_confirmado:
        raise HTTPException(
            status_code=403,
            detail="E-mail não confirmado. Confirme seu e-mail antes de fazer login."
        )

    access_token, refresh_token = create_tokens(empresa.email)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

# ==========================================
# REFRESH TOKEN
# ==========================================
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
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

# ==========================================
# RECUPERAR SENHA
# ==========================================
class RecuperarSenhaRequest(BaseModel):
    email: str

@router.post("/recuperar-senha")
async def recuperar_senha(dados: RecuperarSenhaRequest, db: Session = Depends(banco_dados.get_db)):
    empresa = db.query(Empresa).filter(Empresa.email == dados.email).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="E-mail não encontrado")

    token = create_confirmation_token(dados.email)
    link = f"{FRONT_URL}/redefinir-senha?token={token}"

    await enviar_email_recuperacao(dados.email, link)

    return {"msg": "Link de recuperação enviado para seu e-mail"}

# ==========================================
# REDEFINIR SENHA
# ==========================================
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
