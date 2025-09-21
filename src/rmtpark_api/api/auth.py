from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel

from ..database import banco_dados
from ..database.modelos import Empresa
from ..schemas.empresa import EmpresaCreate, EmpresaOut, hash_password, verify_password
from ..utils.token_utils import create_confirmation_token, verify_confirmation_token
from ..utils.email_utils import enviar_email_confirmacao, enviar_email_recuperacao

router = APIRouter(prefix="/auth", tags=["auth"])


# ============================
#  CADASTRAR EMPRESA
# ============================
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

    # envia email de confirmação
    token = create_confirmation_token(nova_empresa.email)
    link = f"http://localhost:4200/confirmar-email?token={token}"
    await enviar_email_confirmacao(nova_empresa.email, link)

    return nova_empresa


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


# ============================
#  LOGIN
# ============================
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(banco_dados.get_db)):
    empresa = db.query(Empresa).filter(Empresa.email == form_data.username).first()
    if not empresa or not verify_password(form_data.password, empresa.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    # ❌ VERIFICAÇÃO DO EMAIL
    if not empresa.email_confirmado:
        raise HTTPException(
            status_code=403,
            detail="E-mail não confirmado. Por favor, confirme seu e-mail antes de fazer login."
        )

    # cria token JWT de acesso
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode = {"sub": empresa.email, "exp": expire}
    SECRET_KEY = "supersecret"  # substitua pelo valor do .env
    token = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

    return {"access_token": token, "token_type": "bearer"}



# ============================
#  RECUPERAR SENHA
# ============================
class RecuperarSenhaRequest(BaseModel):
    email: str


@router.post("/recuperar-senha")
async def recuperar_senha(dados: RecuperarSenhaRequest, db: Session = Depends(banco_dados.get_db)):
    empresa = db.query(Empresa).filter(Empresa.email == dados.email).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="E-mail não encontrado")

    token = create_confirmation_token(dados.email)
    link = f"http://localhost:4200/redefinir-senha?token={token}"

    # envia email de recuperação
    await enviar_email_recuperacao(dados.email, link)

    return {"msg": "Link de recuperação enviado para seu e-mail"}


# ============================
#  REDEFINIR SENHA
# ============================
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
