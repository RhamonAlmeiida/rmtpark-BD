from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..schemas.relatorio import RelatorioResponse, RelatorioCreate
from ..database.banco_dados import get_db
from ..database import modelos
# importar get_current_empresa do seu módulo auth (ajuste caminho se necessário)
from .auth import get_current_empresa
from ..database.modelos import Empresa

router = APIRouter(prefix="", tags=["Relatórios"])

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
    # base: relatórios apenas da empresa logada
    query = db.query(modelos.Relatorio).filter(modelos.Relatorio.empresa_id == empresa.id)

    if placa:
        query = query.filter(modelos.Relatorio.placa.ilike(f"%{placa}%"))
    if tipo:
        query = query.filter(modelos.Relatorio.tipo.ilike(f"%{tipo}%"))
    if forma_pagamento:
        query = query.filter(modelos.Relatorio.forma_pagamento.ilike(f"%{forma_pagamento}%"))
    if start and end:
        # garante que start <= data_hora_entrada <= end
        query = query.filter(modelos.Relatorio.data_hora_entrada >= start, modelos.Relatorio.data_hora_entrada <= end)
    elif start:
        query = query.filter(modelos.Relatorio.data_hora_entrada >= start)
    elif end:
        query = query.filter(modelos.Relatorio.data_hora_entrada <= end)

    return query.order_by(modelos.Relatorio.data_hora_entrada.desc()).all()

@router.post("/", response_model=RelatorioResponse)
def criar_relatorio(relatorio: RelatorioCreate, db: Session = Depends(get_db), empresa: Empresa = Depends(get_current_empresa)):
    db_relatorio = modelos.Relatorio(**relatorio.dict(), empresa_id=empresa.id)
    db.add(db_relatorio)
    db.commit()
    db.refresh(db_relatorio)
    return db_relatorio

@router.delete("/{relatorio_id}")
def deletar_relatorio(relatorio_id: int, db: Session = Depends(get_db), empresa: Empresa = Depends(get_current_empresa)):
    relatorio = db.query(modelos.Relatorio).filter(modelos.Relatorio.id == relatorio_id, modelos.Relatorio.empresa_id == empresa.id).first()
    if not relatorio:
        raise HTTPException(status_code=404, detail="Relatório não encontrado ou não pertence à sua empresa")
    db.delete(relatorio)
    db.commit()
    return {"mensagem": "Relatório excluído com sucesso"}
