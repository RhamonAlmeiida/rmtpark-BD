from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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
    valorHora: float
    valorDiaria: float
    valorMensalista: float
    arredondamento: int
    formaPagamento: Optional[str] = None
