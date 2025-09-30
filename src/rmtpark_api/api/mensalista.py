from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database.banco_dados import get_db
from ..database import modelos
from .. import schemas

router = APIRouter(prefix="/mensalistas", tags=["Mensalistas"])


@router.post("/", response_model=schemas.Mensalista)
def criar_mensalista(mensalista: schemas.MensalistaCreate, db: Session = Depends(get_db)):
    novo = modelos.Mensalista(**mensalista.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/", response_model=list[schemas.Mensalista])
def listar_mensalistas(db: Session = Depends(get_db)):
    return db.query(modelos.Mensalista).all()


@router.delete("/{id}")
def deletar_mensalista(id: int, db: Session = Depends(get_db)):
    db.query(modelos.Mensalista).filter(modelos.Mensalista.id == id).delete()
    db.commit()
    return {"ok": True}
