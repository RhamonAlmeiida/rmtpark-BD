from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VagaBase(BaseModel):
    placa: str
    tipo: str
    data_hora: Optional[datetime] = Field(default=None, alias="data_hora")

    class Config:
        from_attributes = True   # substitui orm_mode
        populate_by_name = True  # substitui allow_population_by_field_name


class VagaCreate(VagaBase):
    pass


class VagaResponse(VagaBase):
    id: int
    empresa_id: int

    class Config:
        from_attributes = True
