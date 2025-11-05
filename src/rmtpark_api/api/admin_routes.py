# src/rmtpark_api/api/admin_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..database import banco_dados
from ..database import modelos
from ..utils.security import require_admin

router = APIRouter(tags=["admin"])

limites_por_plano = {
    "Basico": 50,
    "Profissional": 150,
    "Empresarial": "Ilimitado"
}

@router.get("/empresas")
def listar_empresas(db: Session = Depends(banco_dados.get_db), _admin=Depends(require_admin)):
    empresas = db.query(modelos.Empresa).all()
    retorno = []
    now = datetime.now()

    for e in empresas:
        total_veiculos = db.query(modelos.Vaga).filter(modelos.Vaga.empresa_id == e.id).count()
        ativa = bool(e.data_expiracao and e.data_expiracao > now)

        plano_titulo = e.plano_titulo
        limite_vagas = limites_por_plano.get(plano_titulo, 0)  # pega o limite baseado no título do plano

        retorno.append({
            "id": e.id,
            "nome": e.nome,
            "cnpj": e.cnpj,
            "email": e.email,
            "plano": {"titulo": plano_titulo},
            "limite_vagas": limite_vagas,
            "data_expiracao": e.data_expiracao,
            "ativa": ativa,
            "confirmado": e.email_confirmado,
            "total_veiculos": total_veiculos,
            "email_confirmado": e.email_confirmado
        })

    return retorno


@router.put("/empresas/{empresa_id}/confirma")
def confirma_email(empresa_id: int, db: Session = Depends(banco_dados.get_db), _admin=Depends(require_admin)):
    empresa = db.query(modelos.Empresa).filter(modelos.Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    empresa.email_confirmado = True  # supondo que exista este campo
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return {"message": "E-mail confirmado com sucesso"}


@router.put("/empresas/{empresa_id}/renovar")
def renovar_plano(empresa_id: int, db: Session = Depends(banco_dados.get_db), _admin=Depends(require_admin)):
    empresa = db.query(modelos.Empresa).filter(modelos.Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    now = datetime.now()
    if empresa.data_expiracao and empresa.data_expiracao > now:
        empresa.data_expiracao = empresa.data_expiracao + timedelta(days=30)
    else:
        empresa.data_expiracao = now + timedelta(days=30)
    db.add(empresa); db.commit(); db.refresh(empresa)
    return {"message": "Plano renovado por +30 dias", "nova_data_expiracao": empresa.data_expiracao}

@router.delete("/empresas/{empresa_id}")
def excluir_empresa(empresa_id: int, db: Session = Depends(banco_dados.get_db), _admin=Depends(require_admin)):
    empresa = db.query(modelos.Empresa).filter(modelos.Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    db.delete(empresa); db.commit()
    return {"message": "Empresa removida"}
