from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from src.rmtpark_api.utils.timezone_utils import agora_sp


class VagaCreate(BaseModel):
    placa: str
    tipo: str
    data_hora: Optional[datetime] = Field(default_factory=agora_sp)

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


class VagaSaidaSchema(BaseModel):
    saida: Optional[datetime] = Field(default_factory=agora_sp)
    duracao: Optional[str] = None
    valor: Optional[float] = None
    formaPagamento: Optional[str] = None

    model_config = {
        "from_attributes": True,
        "validate_by_name": True
    }


class VagaSaidaResponse(BaseModel):
    id: int
    placa: str
    tipo: str
    data_hora_entrada: datetime = Field(default_factory=agora_sp)
    data_hora_saida: datetime = Field(default_factory=agora_sp)
    duracao: str
    valor_pago: float
    forma_pagamento: Optional[str]
    status_pagamento: str
    empresa_id: int

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


class VagaResponse(BaseModel):
    id: int
    numero_interno: Optional[int] = None
    placa: str
    tipo: str
    data_hora: datetime = Field(default_factory=agora_sp)
    data_hora_saida: Optional[datetime] = None
    duracao: Optional[str]
    valor_pago: Optional[float]
    forma_pagamento: Optional[str]
    empresa_id: int

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


class RelatorioResponse(BaseModel):
    id: int
    numero_interno: Optional[int] = None
    placa: str
    tipo: str
    data_hora_entrada: datetime = Field(default_factory=agora_sp)
    data_hora_saida: datetime = Field(default_factory=agora_sp)
    duracao: str
    valor_pago: float
    forma_pagamento: Optional[str] = None
    status_pagamento: str
    empresa_id: int

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


class ConfigSchema(BaseModel):
    valor_hora: float = Field(..., alias="valorHora")
    valor_diaria: float = Field(..., alias="valorDiaria")
    valor_mensalista: float = Field(..., alias="valorMensalista")
    arredondamento: int
    forma_pagamento: str = Field(..., alias="formaPagamento")

    model_config = {
        "from_attributes": True,
        "validate_by_name": True
    }
