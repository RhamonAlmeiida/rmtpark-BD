from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from ..schemas.relatorio import RelatorioResponse, RelatorioCreate
from ..schemas.vaga import ConfigSchema
from ..database.banco_dados import get_db
from ..database import modelos
from ..database.modelos import Empresa
from .auth import get_current_empresa

router = APIRouter(prefix="", tags=["Relatórios"])

@router.get("/", response_model=List[RelatorioResponse])
@router.get("/", response_model=List[RelatorioResponse])
def listar_relatorios(
    placa: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    forma_pagamento: Optional[str] = Query(None),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    empresa: Empresa = Depends(get_current_empresa)
):
    query = db.query(modelos.Relatorio).filter(modelos.Relatorio.empresa_id == empresa.id)

    if placa:
        query = query.filter(modelos.Relatorio.placa.ilike(f"%{placa}%"))
    if tipo:
        query = query.filter(modelos.Relatorio.tipo.ilike(f"%{tipo}%"))
    if forma_pagamento:
        query = query.filter(modelos.Relatorio.forma_pagamento.ilike(f"%{forma_pagamento}%"))
    if start and end:
        query = query.filter(modelos.Relatorio.data_hora_entrada >= start,
                             modelos.Relatorio.data_hora_entrada <= end)
    elif start:
        query = query.filter(modelos.Relatorio.data_hora_entrada >= start)
    elif end:
        query = query.filter(modelos.Relatorio.data_hora_entrada <= end)

    # Ordena pelo mais recente primeiro (decrescente)
    query = query.order_by(modelos.Relatorio.data_hora_saida.desc())

    return query.all()

@router.post("/", response_model=RelatorioResponse)
def criar_relatorio(
    relatorio: RelatorioCreate,
    db: Session = Depends(get_db),
    empresa: Empresa = Depends(get_current_empresa)
):
    db_relatorio = modelos.Relatorio(**relatorio.dict(), empresa_id=empresa.id)
    db.add(db_relatorio)
    db.commit()
    db.refresh(db_relatorio)
    return db_relatorio

@router.delete("/{relatorio_id}")
def deletar_relatorio(
    relatorio_id: int,
    db: Session = Depends(get_db),
    empresa: Empresa = Depends(get_current_empresa)
):
    relatorio = db.query(modelos.Relatorio).filter(
        modelos.Relatorio.id == relatorio_id,
        modelos.Relatorio.empresa_id == empresa.id
    ).first()

    if not relatorio:
        raise HTTPException(status_code=404, detail="Relatório não encontrado ou não pertence à sua empresa")

    db.delete(relatorio)
    db.commit()
    return {"mensagem": "Relatório excluído com sucesso"}

@router.get("/dashboard")
def get_dashboard_data(
    inicio: Optional[datetime] = Query(None),
    fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    empresa: Empresa = Depends(get_current_empresa)
):
    query_base = db.query(modelos.Relatorio).filter(modelos.Relatorio.empresa_id == empresa.id)

    if inicio:
        query_base = query_base.filter(modelos.Relatorio.data_hora_entrada >= inicio)
    if fim:
        query_base = query_base.filter(modelos.Relatorio.data_hora_entrada <= fim)

    total_relatorios = query_base.count()
    total_receita = query_base.with_entities(func.sum(modelos.Relatorio.valor_pago)).scalar() or 0

    receita_por_mes = (
        db.query(
            func.strftime("%Y-%m", modelos.Relatorio.data_hora_saida).label("mes"),
            func.sum(modelos.Relatorio.valor_pago).label("total")
        )
        .filter(modelos.Relatorio.empresa_id == empresa.id)
        .group_by("mes")
        .all()
    )

    dias_movimentados = (
        db.query(
            func.strftime("%Y-%m-%d", modelos.Relatorio.data_hora_entrada).label("dia"),
            func.count(modelos.Relatorio.id).label("quantidade")
        )
        .filter(modelos.Relatorio.empresa_id == empresa.id)
        .group_by("dia")
        .order_by(func.count(modelos.Relatorio.id).desc())
        .limit(5)
        .all()
    )

    horarios_pico = (
        db.query(
            func.strftime("%H", modelos.Relatorio.data_hora_entrada).label("hora"),
            func.count(modelos.Relatorio.id).label("quantidade")
        )
        .filter(modelos.Relatorio.empresa_id == empresa.id)
        .group_by("hora")
        .order_by(func.count(modelos.Relatorio.id).desc())
        .limit(5)
        .all()
    )

    return {
        "total_relatorios": total_relatorios,
        "total_receita": total_receita,
        "receita_por_mes": receita_por_mes,
        "dias_movimentados": dias_movimentados,
        "horarios_pico": horarios_pico
    }
