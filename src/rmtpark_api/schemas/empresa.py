from pydantic import BaseModel, EmailStr, Field, constr
from pwdlib import PasswordHash
from pydantic import validator


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return  password_hash.hash(password)




def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto puro bate com o hash"""
    return  password_hash.verify(plain_password, hashed_password)



class EmpresaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telefone: str = Field(..., min_length=8, max_length=20)
    cnpj: str  # remover o regex fixo

    @validator("cnpj")
    def validar_cnpj(cls, value):
        from validate_docbr import CNPJ
        cnpj = CNPJ()
        # Remove caracteres não numéricos
        somente_numeros = ''.join(filter(str.isdigit, value))
        if not cnpj.validate(somente_numeros):
            raise ValueError("CNPJ inválido")
        return somente_numeros  # ou retorne com máscara se quiser

class EmpresaCreate(EmpresaBase):
    senha: str = Field(..., min_length=6, max_length=20)  # recebida em texto puro na criação


class EmpresaOut(EmpresaBase):
    id: int
    email_confirmado: bool

    model_config = {
        "from_attributes": True
    }
