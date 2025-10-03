from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MensalistaBase(BaseModel):
    nome: str
    cpf: str
    veiculo: str
    placa: str
    validade: datetime
    status: str
    cor: Optional[str] = None

class MensalistaCreate(MensalistaBase):
    pass   # 👈 já herda tudo de MensalistaBase

class Mensalista(MensalistaBase):
    id: int

    class Config:
        from_attributes = True   # Pydantic v2
