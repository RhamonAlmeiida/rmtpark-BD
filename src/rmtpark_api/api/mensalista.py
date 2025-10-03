from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.rmtpark_api.database.banco_dados import get_db
from src.rmtpark_api.database import modelos as models

from src.rmtpark_api.schemas import mensalista as schemas

router = APIRouter()

@router.post("/", response_model=schemas.Mensalista)
def criar_mensalista(mensalista: schemas.MensalistaCreate, db: Session = Depends(get_db)):
    novo = models.Mensalista(**mensalista.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/", response_model=list[schemas.Mensalista])
def listar_mensalistas(db: Session = Depends(get_db)):
    return db.query(models.Mensalista).all()

@router.delete("/{id}")
def deletar_mensalista(id: int, db: Session = Depends(get_db)):
    db.query(models.Mensalista).filter(models.Mensalista.id == id).delete()
    db.commit()
    return {"ok": True}
