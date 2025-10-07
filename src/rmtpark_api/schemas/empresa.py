from pydantic import BaseModel, EmailStr, Field, validator
from pwdlib import PasswordHash
from typing import List

# Configuração do hash de senha
password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """Gera hash seguro da senha"""
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto puro bate com o hash"""
    return password_hash.verify(plain_password, hashed_password)


# -------------------------------
# MODELOS
# -------------------------------

# Modelo de Plano
class Plano(BaseModel):
    titulo: str
    preco: str
    recursos: List[str]
    destaque: bool

    model_config = {
        "from_attributes": True  # permite criar Plano a partir de atributos ORM
    }

# Modelo base de Empresa
class EmpresaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telefone: str = Field(..., min_length=8, max_length=20)
    cnpj: str
    senha: str
    plano: Plano

    @validator("cnpj")
    def validar_cnpj(cls, value: str) -> str:
        from validate_docbr import CNPJ
        cnpj = CNPJ()
        somente_numeros = ''.join(filter(str.isdigit, value))
        if not cnpj.validate(somente_numeros):
            raise ValueError("CNPJ inválido")
        return somente_numeros

    model_config = {
        "from_attributes": True  # permite criar a partir de ORM
    }

# Modelo para criação de empresa (senha em texto puro)
class EmpresaCreate(EmpresaBase):
    senha: str = Field(..., min_length=6, max_length=20)

# Modelo para retorno (sem expor senha)
class EmpresaOut(BaseModel):
    id: int
    nome: str
    email: EmailStr
    telefone: str
    cnpj: str
    email_confirmado: bool
    plano: Plano

    model_config = {
        "from_attributes": True
    }
