from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from src.rmtpark_api.utils.timezone_utils import agora_sp


class MensalistaBase(BaseModel):
    nome: str
    cpf: str
    veiculo: str
    placa: str
    validade: datetime = Field(default_factory=agora_sp)
    status: str = "ativo"          # padrão "ativo"
    cor: Optional[str] = None

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


class MensalistaCreate(MensalistaBase):
    pass


class Mensalista(MensalistaBase):
    id: int
    empresa_id: int

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }
