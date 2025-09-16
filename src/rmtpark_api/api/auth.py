from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext
from src.rmtpark_api.schemas.empresa import EmpresaCreate


from src.rmtpark_api.database import banco_dados
from src.rmtpark_api.database.modelos import Empresa

router = APIRouter(prefix="/auth", tags=["Auth"])

# Configurações JWT
SECRET_KEY = "sua_chave_secreta_aqui"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔒 Funções de senha
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verificar_senha(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 🔑 Token
def criar_token_acesso(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ================================
# Rotas
# ================================
@router.post("/cadastrar")
def register(dados: EmpresaCreate, db: Session = Depends(banco_dados.get_db)):
    empresa_existente = db.query(Empresa).filter(Empresa.cnpj == dados.cnpj).first()
    if empresa_existente:
        raise HTTPException(status_code=400, detail="CNPJ já cadastrado")

    nova_empresa = Empresa(
        nome=dados.nome,
        cnpj=dados.cnpj,
        email=dados.email,
        senha=hash_password(dados.senha),
    )
    db.add(nova_empresa)
    db.commit()
    db.refresh(nova_empresa)

    return {"msg": "Empresa cadastrada com sucesso", "empresa": nova_empresa.nome}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(banco_dados.get_db)):
    empresa = db.query(Empresa).filter(Empresa.email == form_data.username).first()
    if not empresa or not verificar_senha(form_data.password, empresa.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = criar_token_acesso(
        data={"sub": empresa.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
