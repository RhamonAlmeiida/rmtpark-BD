from pydantic import BaseModel
from typing import Optional

class MensalistaBase(BaseModel):
    nome: str
    placa: str
    veiculo: str
    cor: str
    cpf: str
    validade: str
    status: str

class MensalistaCreate(MensalistaBase):
    pass

class Mensalista(MensalistaBase):
    id: int

    class Config:
        orm_mode = True
