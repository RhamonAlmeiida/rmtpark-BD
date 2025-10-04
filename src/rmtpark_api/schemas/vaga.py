from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# ------------------- CRIAÇÃO -------------------
class VagaCreate(BaseModel):
    placa: str
    tipo: str
    data_hora: Optional[datetime] = None   # opcional (pode vir null)

    class Config:
        orm_mode = True


# ------------------- SAÍDA -------------------
class VagaSaidaSchema(BaseModel):
    saida: Optional[datetime] = None
    duracao: Optional[str] = None
    valor: Optional[float] = None
    formaPagamento: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class VagaSaidaResponse(BaseModel):
    id: int
    placa: str
    tipo: str
    data_hora_entrada: datetime
    data_hora_saida: datetime
    duracao: str
    valor_pago: float
    forma_pagamento: Optional[str]
    status_pagamento: str
    empresa_id: int

    class Config:
        orm_mode = True
# ------------------- RESPOSTA -------------------
class VagaResponse(BaseModel):
    id: int
    placa: str
    tipo: str
    data_hora: datetime
    data_hora_saida: Optional[datetime]
    duracao: Optional[str]
    valor_pago: Optional[float]
    forma_pagamento: Optional[str]
    empresa_id: int

    class Config:
        orm_mode = True


# --- Schemas Relatorio ---
class RelatorioResponse(BaseModel):
    id: int
    placa: str
    tipo: str
    data_hora_entrada: datetime
    data_hora_saida: datetime
    duracao: str
    valor_pago: float
    forma_pagamento: Optional[str] = None
    status_pagamento: str
    empresa_id: int

    class Config:
        orm_mode = True

# --- Schemas Configuracoes ---
class ConfigSchema(BaseModel):
    valor_hora: float = Field(..., alias="valorHora")
    valor_diaria: float = Field(..., alias="valorDiaria")
    valor_mensalista: float = Field(..., alias="valorMensalista")
    arredondamento: int
    forma_pagamento: str = Field(..., alias="formaPagamento")

    model_config = {
        "from_attributes": True,     # antigo orm_mode
        "validate_by_name": True     # antigo allow_population_by_field_name
    }