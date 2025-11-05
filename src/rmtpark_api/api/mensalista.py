from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.rmtpark_api.database.banco_dados import get_db
from src.rmtpark_api.database import modelos as models
from src.rmtpark_api.api.auth import get_current_empresa
from src.rmtpark_api.schemas import mensalista as schemas
from src.rmtpark_api.utils.timezone_utils import agora_sp

router = APIRouter()

# -------------------------------
# Criar Mensalista
# -------------------------------
@router.post("/", response_model=schemas.Mensalista)
def criar_mensalista(
    mensalista: schemas.MensalistaCreate,
    db: Session = Depends(get_db),
    empresa_logada: models.Empresa = Depends(get_current_empresa)
):
    # Ajusta validade para o timezone de SP, caso não seja enviado
    if not mensalista.validade:
        mensalista.validade = agora_sp()

    # Verifica se a placa já existe para a empresa
    existente = db.query(models.Mensalista).filter_by(
        placa=mensalista.placa,
        empresa_id=empresa_logada.id
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Mensalista com esta placa já existe para esta empresa.")

    try:
        novo = models.Mensalista(**mensalista.dict(), empresa_id=empresa_logada.id)
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar mensalista: {e}")

# -------------------------------
# Listar Mensalistas da Empresa
# -------------------------------
@router.get("/", response_model=list[schemas.Mensalista])
def listar_mensalistas(
    db: Session = Depends(get_db),
    empresa_logada: models.Empresa = Depends(get_current_empresa)
):
    mensalistas = db.query(models.Mensalista).filter_by(empresa_id=empresa_logada.id).all()
    return mensalistas

# -------------------------------
# Deletar Mensalista pelo ID
# -------------------------------
@router.delete("/{id}")
def deletar_mensalista(id: int, db: Session = Depends(get_db), empresa_logada: models.Empresa = Depends(get_current_empresa)):
    mensalista = db.query(models.Mensalista).filter_by(id=id, empresa_id=empresa_logada.id).first()
    if not mensalista:
        raise HTTPException(status_code=404, detail="Mensalista não encontrado ou não pertence à sua empresa.")
    db.delete(mensalista)
    db.commit()
    return {"ok": True}
