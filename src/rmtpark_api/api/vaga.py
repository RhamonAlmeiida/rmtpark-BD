from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import pytz
from ..database import modelos
from ..database.banco_dados import get_db
from ..schemas import vaga as vaga_schema
from ..utils.security import get_current_empresa

router = APIRouter(tags=["vagas"])

Vaga = modelos.Vaga
Relatorio = modelos.Relatorio  # Certifique-se que este modelo exista

# ------------------- CRIAR VAGA -------------------
@router.post("/", response_model=vaga_schema.VagaResponse)
def criar_vaga(
    vaga: vaga_schema.VagaCreate,
    db: Session = Depends(get_db),
    empresa_logada: modelos.Empresa = Depends(get_current_empresa)
):
    nova_vaga = Vaga(
        placa=vaga.placa.upper(),
        tipo=vaga.tipo,
        data_hora=vaga.data_hora.replace(tzinfo=None) if vaga.data_hora else None,
        empresa_id=empresa_logada.id
    )
    db.add(nova_vaga)
    db.commit()
    db.refresh(nova_vaga)
    return nova_vaga


# ------------------- BUSCAR VAGA -------------------
@router.get("/{vaga_id}", response_model=vaga_schema.VagaResponse)
def buscar_vaga(
    vaga_id: int,
    db: Session = Depends(get_db),
    empresa_logada: modelos.Empresa = Depends(get_current_empresa)
):
    vaga = db.query(Vaga).filter(
        Vaga.id == vaga_id,
        Vaga.empresa_id == empresa_logada.id
    ).first()
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    return vaga

# ------------------- LISTAR VAGAS -------------------
@router.get("/", response_model=List[vaga_schema.VagaResponse])
def listar_vagas(
    db: Session = Depends(get_db),
    empresa_logada: modelos.Empresa = Depends(get_current_empresa)
):
    return db.query(Vaga).filter(
        Vaga.empresa_id == empresa_logada.id
    ).all()

# ------------------- DELETAR VAGA -------------------
@router.delete("/{vaga_id}")
def deletar_vaga(
    vaga_id: int,
    db: Session = Depends(get_db),
    empresa_logada: modelos.Empresa = Depends(get_current_empresa)
):
    vaga = db.query(Vaga).filter(
        Vaga.id == vaga_id,
        Vaga.empresa_id == empresa_logada.id
    ).first()
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")

    db.delete(vaga)
    db.commit()
    return {"detail": "Vaga removida com sucesso"}

# ------------------- REGISTRAR SAÍDA -------------------
from pydantic import BaseModel

class VagaSaidaSchema(BaseModel):
    saida: str
    duracao: str
    valor: float
    formaPagamento: str

@router.put("/{vaga_id}/saida", response_model=vaga_schema.VagaResponse)
def registrar_saida(
    vaga_id: int,
    dados: VagaSaidaSchema,
    db: Session = Depends(get_db),
    empresa_logada: modelos.Empresa = Depends(get_current_empresa)
):
    vaga = db.query(Vaga).filter(
        Vaga.id == vaga_id,
        Vaga.empresa_id == empresa_logada.id
    ).first()
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")

    # Atualiza vaga com os dados enviados pelo front
    vaga.data_hora_saida = dados.saida
    vaga.duracao = dados.duracao
    vaga.valor_pago = dados.valor
    vaga.forma_pagamento = dados.formaPagamento
    vaga.status_pagamento = "Pago"

    # Cria registro no relatório
    relatorio = Relatorio(
        placa=vaga.placa,
        tipo=vaga.tipo,
        data_hora_entrada=vaga.data_hora,
        data_hora_saida=vaga.data_hora_saida,
        duracao=vaga.duracao,
        valor_pago=vaga.valor_pago,
        forma_pagamento=vaga.forma_pagamento,
        status_pagamento=vaga.status_pagamento,
        empresa_id=vaga.empresa_id
    )
    db.add(relatorio)
    db.commit()
    db.refresh(vaga)

    return vaga
