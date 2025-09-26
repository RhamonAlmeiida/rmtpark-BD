from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# Base para criação de relatório
class RelatorioBase(BaseModel):
    placa: str
    tipo: str
    data_hora_entrada: Optional[datetime] = None
    data_hora_saida: Optional[datetime] = None
    duracao: Optional[str] = None
    valor_pago: Optional[float] = None
    forma_pagamento: Optional[str] = None
    status_pagamento: Optional[str] = None

# Schema usado para criar um relatório (entrada no banco)
class RelatorioCreate(RelatorioBase):
    pass

# Schema de saída para retornar relatório
class RelatorioResponse(RelatorioBase):
    id: int
    model_config = {
        "from_attributes": True  # substitui orm_mode = True
    }
