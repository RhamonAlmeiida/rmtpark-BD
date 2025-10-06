from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MensalistaBase(BaseModel):
    nome: str
    cpf: str
    veiculo: str
    placa: str
    validade: datetime
    status: Optional[str] = "ativo"   # 👈 agora vira opcional com default
    cor: Optional[str] = None
""

class MensalistaCreate(MensalistaBase):
    pass   # 👈 já herda tudo de MensalistaBase

class Mensalista(MensalistaBase):
    id: int
    empresa_id: int

    class Config:
        from_attributes = True   # Pydantic v2
