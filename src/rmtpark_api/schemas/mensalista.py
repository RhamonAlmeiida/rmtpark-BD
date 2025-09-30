# src/rmtpark_api/schemas/mensalista.py
from pydantic import BaseModel

class MensalistaBase(BaseModel):
    nome: str
    cpf: str
    telefone: str | None = None
    veiculo: str | None = None
    placa: str | None = None

class MensalistaCreate(MensalistaBase):
    pass

class Mensalista(MensalistaBase):
    id: int

    class Config:
        from_attributes = True   # 👈 substitui orm_mode no Pydantic v2
