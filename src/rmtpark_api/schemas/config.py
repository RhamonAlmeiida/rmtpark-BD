from pydantic import BaseModel
from typing import Optional


class ConfigSchema(BaseModel):
    valorHora: float = 10.0
    valorDiaria: float = 0.0
    valorMensalista: float = 0.0
    arredondamento: int = 15   # minutos
    formaPagamento: Optional[str] = "Pix"

    class Config:
        orm_mode = True
