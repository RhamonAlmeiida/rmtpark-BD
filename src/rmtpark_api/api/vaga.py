from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.banco_dados import get_db
from ..database import modelos
from ..schemas import vaga as vaga_schema
from ..utils.security import get_current_empresa
from typing import List


# prefixo "/vagas" → todas as rotas vão começar em /api/vagas
router = APIRouter(tags=["vagas"])

# CRIAR VAGA → POST /api/vagas
@router.post("/", response_model=vaga_schema.VagaResponse)
def criar_vaga(
    vaga: vaga_schema.VagaCreate,
    db: Session = Depends(get_db),
    empresa_logada: modelos.Empresa = Depends(get_current_empresa)
):
    nova_vaga = modelos.Vaga(
        placa=vaga.placa.upper(),
        tipo=vaga.tipo,
        data_hora=vaga.data_hora,
        empresa_id=empresa_logada.id  # vincula automaticamente
    )
    db.add(nova_vaga)
    db.commit()
    db.refresh(nova_vaga)
    return nova_vaga

# BUSCAR POR ID → GET /api/vagas/{vaga_id}
@router.get("/{vaga_id}", response_model=vaga_schema.VagaResponse)
def buscar_vaga(vaga_id: int, db: Session = Depends(get_db)):
    vaga = db.query(modelos.Vaga).filter(modelos.Vaga.id == vaga_id).first()
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    return vaga

# GET /api/vagas → lista todas as vagas
@router.get("/", response_model=List[vaga_schema.VagaResponse])
def listar_vagas(db: Session = Depends(get_db), empresa_logada: modelos.Empresa = Depends(get_current_empresa)):
    return db.query(modelos.Vaga).filter(modelos.Vaga.empresa_id == empresa_logada.id).all()


# DELETAR VAGA → DELETE /api/vagas/{vaga_id}
@router.delete("/{vaga_id}")
def deletar_vaga(vaga_id: int, db: Session = Depends(get_db)):
    vaga = db.query(modelos.Vaga).filter(modelos.Vaga.id == vaga_id).first()
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    db.delete(vaga)
    db.commit()
    return {"detail": "Vaga removida com sucesso"}
