from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

# Configuração do Passlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 🔒 Funções utilitárias para senha
def hash_password(password: str) -> str:
    """Gera o hash da senha"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto puro bate com o hash"""
    return pwd_context.verify(plain_password, hashed_password)


# 📌 Schemas Pydantic
class EmpresaBase(BaseModel):
    nome: str
    empresa: str
    email: EmailStr
    telefone: str
    cnpj: str


class EmpresaCreate(EmpresaBase):
    senha: str  # recebida em texto puro na criação


class EmpresaOut(EmpresaBase):
    id: int
    email_confirmado: bool

    class Config:
        from_attributes = True
