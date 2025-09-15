from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import banco_dados
from ..database.modelos import Empresa
from ..schemas.empresa import EmpresaCreate, EmpresaOut, hash_password
from validate_docbr import CNPJ  # pip install validate-docbr

router = APIRouter(prefix="/empresas", tags=["empresas"])

cnpj_validator = CNPJ()


@router.post("/", response_model=EmpresaOut)
def criar_empresa(empresa: EmpresaCreate, db: Session = Depends(banco_dados.get_db)):
    # ✅ validar CNPJ
    if not cnpj_validator.validate(empresa.cnpj):
        raise HTTPException(status_code=400, detail="CNPJ inválido")

    # ✅ verificar se email já existe
    if db.query(Empresa).filter(Empresa.email == empresa.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # ✅ verificar se cnpj já existe
    if db.query(Empresa).filter(Empresa.cnpj == empresa.cnpj).first():
        raise HTTPException(status_code=400, detail="CNPJ já cadastrado")

    # ✅ hash da senha
    hashed_senha = hash_password(empresa.senha)

    nova_empresa = Empresa(
        nome=empresa.nome,
        empresa=empresa.empresa,
        email=empresa.email,
        telefone=empresa.telefone,
        cnpj=empresa.cnpj,
        senha=hashed_senha,
        email_confirmado=False,
    )

    db.add(nova_empresa)
    db.commit()
    db.refresh(nova_empresa)

    # TODO: enviar email de confirmação futuramente
    return nova_empresa
