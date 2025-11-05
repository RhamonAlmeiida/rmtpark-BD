from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.rmtpark_api.database.banco_dados import get_db
from src.rmtpark_api.database import modelos as models
from src.rmtpark_api.api.auth import get_current_empresa
from src.rmtpark_api.schemas import mensalista as schemas

router = APIRouter()

from fastapi import HTTPException

@router.post("/", response_model=schemas.Mensalista)
def criar_mensalista(
    mensalista: schemas.MensalistaCreate,
    db: Session = Depends(get_db),
    empresa_logada: models.Empresa = Depends(get_current_empresa)
):
    try:
        novo = models.Mensalista(**mensalista.dict(), empresa_id=empresa_logada.id)
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar mensalista: {e}")



@router.get("/", response_model=list[schemas.Mensalista])
def listar_mensalistas(
    db: Session = Depends(get_db),
    empresa_logada: models.Empresa = Depends(get_current_empresa)
):
    return db.query(models.Mensalista).filter_by(empresa_id=empresa_logada.id).all()

@router.delete("/{id}")
def deletar_mensalista(id: int, db: Session = Depends(get_db)):
    db.query(models.Mensalista).filter(models.Mensalista.id == id).delete()
    db.commit()
    return {"ok": True}
