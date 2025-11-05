from pydantic import BaseModel
from typing import Optional

class ConfigSchema(BaseModel):
    valor_hora: float = 10.0
    valor_diaria: float = 0.0
    valor_mensalista: float = 0.0
    arredondamento: int = 15   # minutos
    forma_pagamento: Optional[str] = "Pix"

    model_config = {
        "from_attributes": True,  # permite criar a partir de ORM
        "populate_by_name": True  # equivalente ao allow_population_by_field_name
    }
