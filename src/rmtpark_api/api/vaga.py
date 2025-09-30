from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from typing import Optional
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
    formaPagamento: Optional[str] = None

from datetime import datetime

@router.put("/{vaga_id}/saida", response_model=vaga_schema.VagaResponse)
def registrar_saida(
    vaga_id: int,
    dados: vaga_schema.VagaSaidaSchema,
    db: Session = Depends(get_db),
    empresa_logada: modelos.Empresa = Depends(get_current_empresa)
):
    vaga = db.query(Vaga).filter(
        Vaga.id == vaga_id,
        Vaga.empresa_id == empresa_logada.id
    ).first()

    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")

    # Calcula a saída agora
    saida = datetime.now()
    duracao = saida - vaga.data_hora  # timedelta
    duracao_str = str(duracao)  # ex: "1:32:05"

    # Calcula o valor (exemplo: R$ 5,00 por hora)
    horas = duracao.total_seconds() / 3600
    valor = round(horas * 5, 2) if vaga.tipo == "Diarista" else 0.0

    vaga.data_hora_saida = saida
    vaga.duracao = duracao_str
    vaga.valor_pago = valor
    vaga.forma_pagamento = dados.formaPagamento
    vaga.status_pagamento = "Pago" if vaga.tipo == "Diarista" else "Mensalista"

    relatorio = Relatorio(
        placa=vaga.placa,
        tipo=vaga.tipo,
        data_hora_entrada=vaga.data_hora,
        data_hora_saida=saida,
        duracao=duracao_str,
        valor_pago=valor,
        forma_pagamento=dados.formaPagamento,
        status_pagamento=vaga.status_pagamento,
        empresa_id=vaga.empresa_id
    )

    db.add(relatorio)
    db.commit()
    db.refresh(relatorio)

    db.delete(vaga)
    db.commit()

    return relatorio
