from pydantic import BaseModel, EmailStr, Field, constr
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
    nome: str = Field(..., min_length=2, max_length=100)
    empresa: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telefone: str = Field(..., min_length=8, max_length=20)
    cnpj: constr(pattern=r"^\d{14}$")  # exatamente 14 dígitos


class EmpresaCreate(EmpresaBase):
    senha: str = Field(..., min_length=6, max_length=100)  # recebida em texto puro na criação


class EmpresaOut(EmpresaBase):
    id: int
    email_confirmado: bool

    model_config = {
        "from_attributes": True
    }
