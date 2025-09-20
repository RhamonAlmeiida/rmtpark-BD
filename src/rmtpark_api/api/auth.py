from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext
import asyncio
import os

from src.rmtpark_api.schemas.empresa import EmpresaCreate
from src.rmtpark_api.database import banco_dados
from src.rmtpark_api.database.modelos import Empresa
from src.rmtpark_api.utils.email_utils import enviar_email_confirmacao  # 👈 importar utilitário de e-mail

router = APIRouter(prefix="/auth", tags=["Auth"])

# ------------------ Config ------------------
SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_aqui")  # 🔑 melhor usar .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ------------------ Funções utilitárias ------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verificar_senha(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def criar_token_acesso(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def criar_token_confirmacao(email: str):
    """Cria token temporário para confirmar e-mail"""
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = {"sub": email, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ------------------ Rotas ------------------
@router.post("/cadastrar")
def cadastrar(dados: EmpresaCreate, db: Session = Depends(banco_dados.get_db)):
    empresa_existente = db.query(Empresa).filter(Empresa.cnpj == dados.cnpj).first()
    if empresa_existente:
        raise HTTPException(status_code=400, detail="CNPJ já cadastrado")

    nova_empresa = Empresa(
        nome=dados.nome,
        cnpj=dados.cnpj,
        email=dados.email,
        telefone=dados.telefone,
        senha=hash_password(dados.senha),
        email_confirmado=False  # 👈 começa como False
    )
    db.add(nova_empresa)
    db.commit()
    db.refresh(nova_empresa)

    # Gerar token de confirmação de e-mail
    token_confirmacao = criar_token_confirmacao(nova_empresa.email)
    link_confirmacao = f"http://localhost:8000/auth/confirmar-email?token={token_confirmacao}"

    # 🔥 Envio do e-mail real
    try:
        asyncio.run(enviar_email_confirmacao(nova_empresa.email, link_confirmacao))
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

    return {"msg": "Empresa cadastrada com sucesso. Confirme seu e-mail para ativar o login."}


@router.get("/confirmar-email")
def confirmar_email(token: str, db: Session = Depends(banco_dados.get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    empresa = db.query(Empresa).filter(Empresa.email == email).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    empresa.email_confirmado = True
    db.commit()

    return {"msg": "E-mail confirmado com sucesso! Agora você pode fazer login."}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(banco_dados.get_db)):
    empresa = db.query(Empresa).filter(Empresa.email == form_data.username).first()
    if not empresa or not verificar_senha(form_data.password, empresa.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    # 🚨 Verifica se o e-mail foi confirmado
    if not empresa.email_confirmado:
        raise HTTPException(status_code=403, detail="Confirme seu e-mail antes de fazer login.")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = criar_token_acesso(
        data={"sub": empresa.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
