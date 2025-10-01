from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import banco_dados
from ..database.modelos import Empresa
from ..schemas.empresa import EmpresaCreate, EmpresaOut, hash_password
from validate_docbr import CNPJ
import logging
router = APIRouter(tags=["empresas"])

cnpj_validator = CNPJ()

logger = logging.getLogger(__name__)
from sqlalchemy.exc import IntegrityError

import traceback

@router.post("/", response_model=EmpresaOut)
def criar_empresa(empresa: EmpresaCreate, db: Session = Depends(banco_dados.get_db)):
    if not cnpj_validator.validate(empresa.cnpj):
        raise HTTPException(status_code=400, detail="CNPJ inválido")

    try:
        hashed_senha = hash_password(empresa.senha)

        nova_empresa = Empresa(
            nome=empresa.nome,
            email=empresa.email,
            telefone=''.join(filter(str.isdigit, empresa.telefone)),  # só números
            cnpj=''.join(filter(str.isdigit, empresa.cnpj)),          # só números
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

    except Exception as e:
        db.rollback()
        print("Erro ao criar empresa:", e)
        print(traceback.format_exc())  # printa stacktrace completo no console
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
