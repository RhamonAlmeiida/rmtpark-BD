from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ------------------- BASE -------------------
class VagaBase(BaseModel):
    placa: str
    tipo: str
    data_hora: Optional[datetime] = Field(default=None, alias="data_hora")  # hora de entrada

    class Config:
        from_attributes = True  # substitui orm_mode no Pydantic v2
        validate_by_name = True

# ------------------- CREATE -------------------
class VagaCreate(VagaBase):
    pass

# ------------------- RESPONSE -------------------
class VagaResponse(VagaBase):
    id: int
    empresa_id: int
    data_hora_saida: Optional[datetime] = None
    duracao: Optional[str] = None
    valor: Optional[float] = None
    forma_pagamento: Optional[str] = None

    class Config:
        from_attributes = True
        validate_by_name = True

# ------------------- SAÍDA -------------------
class VagaSaidaSchema(BaseModel):
    data_hora_saida: datetime
    duracao: str
    valor: float
    forma_pagamento: Optional[str] = None

    class Config:
        from_attributes = True
        validate_by_name = True



class RelatorioResponse(BaseModel):
    id: int
    placa: str
    tipo: str
    dataHoraEntrada: datetime
    dataHoraSaida: Optional[datetime]
    duracao: Optional[str]
    valorPago: float
    formaPagamento: Optional[str] = None
    statusPagamento: str

    class Config:
        orm_mode = True