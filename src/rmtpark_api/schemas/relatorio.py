from datetime import datetime
from pydantic import BaseModel, Field
from src.rmtpark_api.utils.timezone_utils import agora_sp


class RelatorioBase(BaseModel):
    placa: str
    tipo: str
    data_hora_entrada: datetime = Field(default_factory=agora_sp)
    data_hora_saida: datetime = Field(default_factory=agora_sp)
    duracao: str | None = None
    valor_pago: float | None = None
    forma_pagamento: str | None = None
    status_pagamento: str | None = None

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


class RelatorioCreate(RelatorioBase):
    pass


class RelatorioResponse(RelatorioBase):
    id: int

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }
