from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..schemas.relatorio import RelatorioResponse
from ..database.banco_dados import get_db
from ..schemas.relatorio import RelatorioCreate, RelatorioResponse
from ..database import modelos

router = APIRouter(prefix="", tags=["Relatórios"])

@router.get("/", response_model=List[RelatorioResponse])
def listar_relatorios(db: Session = Depends(get_db)):
    return db.query(modelos.Relatorio).all()

@router.post("/", response_model=RelatorioResponse)
def criar_relatorio(relatorio: RelatorioCreate, db: Session = Depends(get_db)):
    db_relatorio = modelos.Relatorio(**relatorio.dict())
    db.add(db_relatorio)
    db.commit()
    db.refresh(db_relatorio)
    return db_relatorio

@router.delete("/{relatorio_id}")
def deletar_relatorio(relatorio_id: int, db: Session = Depends(get_db)):
    relatorio = db.query(modelos.Relatorio).filter(modelos.Relatorio.id == relatorio_id).first()
    if not relatorio:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    db.delete(relatorio)
    db.commit()
    return {"mensagem": "Relatório excluído com sucesso"}
