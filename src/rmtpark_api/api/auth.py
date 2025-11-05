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
from ..utils.token_utils import create_confirmation_token, verify_confirmation_token
from ..utils.email_utils import enviar_email_confirmacao, enviar_email_recuperacao

# -----------------------
# Router
# -----------------------
router = APIRouter(tags=["auth"])

# -----------------------
# JWT Config
# -----------------------
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hora
REFRESH_TOKEN_EXPIRE_DAYS = 7     # 7 dias

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# -----------------------
# ADMIN MASTER FIXO
# -----------------------
ADMIN_EMAIL = "admin@rmtpark.com"
ADMIN_PASSWORD = "admin@123"  # senha fixa — mantenha em ambiente seguro
ADMIN_NAME = "Administrador Master"
is_admin = ADMIN_EMAIL


# Função para pegar empresa logada

def get_current_empresa(
    db: Session = Depends(banco_dados.get_db),
    token: str = Depends(oauth2_scheme)
) -> SimpleNamespace:
    """
    Retorna a empresa autenticada ou admin.
    """
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

# -----------------------
# Cadastro de empresa
# -----------------------
# @router.post("/cadastrar", response_model=EmpresaOut)
# async def cadastrar(empresa: EmpresaCreate, db: Session = Depends(banco_dados.get_db)):
#     # Verifica email e CNPJ duplicados
#     if db.query(Empresa).filter(Empresa.email == empresa.email).first():
#         raise HTTPException(status_code=400, detail="E-mail já cadastrado")
#     if db.query(Empresa).filter(Empresa.cnpj == empresa.cnpj).first():
#         raise HTTPException(status_code=400, detail="CNPJ já cadastrado")
#
#     # Cria nova empresa com senha hash
#     hashed_senha = hash_password(empresa.senha)
#     nova_empresa = Empresa(
#         nome=empresa.nome,
#         email=empresa.email,
#         telefone=''.join(filter(str.isdigit, empresa.telefone)),
#         cnpj=''.join(filter(str.isdigit, empresa.cnpj)),
#         senha=hashed_senha,
#         email_confirmado=False,
#         plano_titulo=empresa.plano.titulo,
#         plano_preco=empresa.plano.preco,
#         plano_recursos=empresa.plano.recursos,
#         plano_destaque=empresa.plano.destaque
#     )
#
#     db.add(nova_empresa)
#     db.commit()
#     db.refresh(nova_empresa)
#
#     # Cria token de confirmação e envia e-mail
#     token = create_confirmation_token(nova_empresa.email)
#     await enviar_email_confirmacao(nova_empresa.email, token)
#
#     return EmpresaOut.model_validate(nova_empresa)

# -----------------------
# Confirmar email
# -----------------------
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

# -----------------------
# Login com access e refresh token
# -----------------------
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_admin: bool = False

def create_tokens(email: str):
    now = datetime.now()

    access_token_expires = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {"sub": email, "exp": access_token_expires},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    refresh_token_expires = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = jwt.encode(
        {"sub": email, "exp": refresh_token_expires, "type": "refresh"},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return access_token, refresh_token

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(banco_dados.get_db)
):
    #login admin
    if  form_data.username == ADMIN_EMAIL and form_data.password == ADMIN_PASSWORD:
        access_token, refresh_token = create_tokens(ADMIN_EMAIL)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "is_admin": True
        }

    #login empresa

    empresa = db.query(Empresa).filter(Empresa.email == form_data.username).first()
    if not empresa or not verify_password(form_data.password, empresa.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not empresa.email_confirmado:
        raise HTTPException(
            status_code=403,
            detail="E-mail não confirmado. Confirme seu e-mail antes de fazer login."
        )

    access_token, refresh_token = create_tokens(empresa.email)
    return {"access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "is_admin": False
    }

# -----------------------
# Refresh token
# -----------------------
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
    is_admin = email == ADMIN_EMAIL
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "is_admin": is_admin
    }


# Recuperar senha

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
