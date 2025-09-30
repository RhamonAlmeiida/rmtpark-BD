from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import banco_dados
from ..database.modelos import Empresa
from ..schemas.empresa import EmpresaCreate, EmpresaOut, hash_password
from validate_docbr import CNPJ  # pip install validate-docbr

router = APIRouter(prefix="/empresas", tags=["empresas"])

cnpj_validator = CNPJ()


from sqlalchemy.exc import IntegrityError

@router.post("/", response_model=EmpresaOut)
def criar_empresa(empresa: EmpresaCreate, db: Session = Depends(banco_dados.get_db)):
    if not cnpj_validator.validate(empresa.cnpj):
        raise HTTPException(status_code=400, detail="CNPJ inválido")

    try:
        hashed_senha = hash_password(empresa.senha)

        nova_empresa = Empresa(
            nome=empresa.nome,
            email=empresa.email,
            telefone=empresa.telefone,
            cnpj=empresa.cnpj,
            senha=hashed_senha,
            email_confirmado=False,
        )

        db.add(nova_empresa)
        db.commit()
        db.refresh(nova_empresa)

        return EmpresaOut.model_validate(nova_empresa)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email ou CNPJ já cadastrado")

