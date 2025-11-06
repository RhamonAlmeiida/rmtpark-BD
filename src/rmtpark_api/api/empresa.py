from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database import banco_dados
from ..database.modelos import Empresa
from ..schemas.empresa import EmpresaCreate, EmpresaOut, hash_password
from validate_docbr import CNPJ
import logging
import traceback
import requests
from datetime import datetime, timedelta
import os
from ..utils.email_utils import enviar_email_confirmacao
from ..utils.token_utils import create_confirmation_token


router = APIRouter(tags=["empresas"])
logger = logging.getLogger(__name__)
cnpj_validator = CNPJ()

# === CONFIGURAÇÃO ASAAS SANDBOX ===
ASAAS_API_KEY = os.getenv("ASAAS_API_KEY")
if not ASAAS_API_KEY:
    raise ValueError("Variável de ambiente ASAAS_API_KEY não encontrada")

if not ASAAS_API_KEY.startswith("$"):
    ASAAS_API_KEY = "$" + ASAAS_API_KEY

ASAAS_API_URL = "https://sandbox.asaas.com/api/v3/"

HEADERS = {
    "access_token": ASAAS_API_KEY,
    "Content-Type": "application/json"
}


# -------------------------------
# Funções de integração com Asaas
# -------------------------------

def criar_cliente_asaas(empresa: Empresa):
    """
    Cria cliente no Asaas Sandbox e retorna o ID
    """
    payload = {
        "name": empresa.nome,
        "email": empresa.email,
        "cpfCnpj": empresa.cnpj,
        "phone": empresa.telefone,
        "externalReference": str(empresa.id)  # opcional
    }
    response = requests.post(f"{ASAAS_API_URL}customers", headers=HEADERS, json=payload)
    data = response.json()
    if response.status_code not in [200, 201]:
        logger.error(f"Erro ao criar cliente Asaas: {data}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar cliente no Asaas: {data}")
    return data.get("id")


def criar_link_pagamento_asaas(cliente_id, empresa: Empresa, dias_vencimento=5):
    """
    Cria cobrança no Asaas e retorna ID, status e link do checkout
    """
    try:
        valor = float(empresa.plano_preco.replace("R$ ", "").replace("/mês", "").replace(",", "."))
    except Exception as e:
        logger.error(f"Erro ao converter valor do plano: {empresa.plano_preco}")
        raise HTTPException(status_code=400, detail=f"Valor do plano inválido: {empresa.plano_preco}") from e

    due_date = (datetime.now() + timedelta(days=dias_vencimento)).strftime("%Y-%m-%d")

    payload = {
        "customer": cliente_id,
        "billingType": "CREDIT_CARD",  # Default
        "value": valor,
        "dueDate": due_date,
        "description": f"Assinatura do plano {empresa.plano_titulo}",
        "externalReference": str(empresa.id),
        "notificationUrl": "https://seusite.com/notificacao-pagamento",
        "billingTypeOptions": ["BOLETO", "CREDIT_CARD", "PIX"]
    }

    response = requests.post(f"{ASAAS_API_URL}payments", headers=HEADERS, json=payload)
    data = response.json()
    if response.status_code not in [200, 201]:
        logger.error(f"Erro ao criar cobrança Asaas: {data}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar cobrança no Asaas: {data}")

    # Link final do checkout
    checkout_link = data.get("invoiceUrl") or data.get("bankSlipUrl") or f"https://sandbox.asaas.com/payment/{data['id']}"
    return data.get("id"), data.get("status"), checkout_link


# -------------------------------
# Endpoints FastAPI
# -------------------------------

@router.post("/", response_model=EmpresaOut)
async def criar_empresa(empresa: EmpresaCreate, db: Session = Depends(banco_dados.get_db), form_data=None):
    """
    Cria nova empresa, registra cliente no Asaas e gera link de pagamento
    """
    # Valida CNPJ
    somente_numeros_cnpj = ''.join(filter(str.isdigit, empresa.cnpj))
    if not cnpj_validator.validate(somente_numeros_cnpj):
        raise HTTPException(status_code=400, detail="CNPJ inválido")

    # Normaliza telefone
    somente_numeros_telefone = ''.join(filter(str.isdigit, empresa.telefone))

    try:
        hashed_senha = hash_password(empresa.senha)

        # Cria empresa no banco
        nova_empresa = Empresa(
            nome=empresa.nome,
            email=empresa.email,
            telefone=somente_numeros_telefone,
            cnpj=somente_numeros_cnpj,
            senha=empresa.senha,
            email_confirmado=False,
            plano_titulo=empresa.plano.titulo,
            plano_preco=empresa.plano.preco,
            plano_recursos=empresa.plano.recursos,
            plano_destaque=empresa.plano.destaque
        )
        db.add(nova_empresa)
        db.commit()
        db.refresh(nova_empresa)

        # Cria cliente Asaas
        cliente_id = criar_cliente_asaas(nova_empresa)

        # Cria link de pagamento (checkout) Asaas
        pagamento_id, pagamento_status, pagamento_link = criar_link_pagamento_asaas(cliente_id, nova_empresa)

        # Salva dados de pagamento no banco
        nova_empresa.pagamento_id = pagamento_id
        nova_empresa.pagamento_status = pagamento_status
        nova_empresa.pagamento_link = pagamento_link
        db.commit()
        db.refresh(nova_empresa)

        token = create_confirmation_token(nova_empresa.email)
        await enviar_email_confirmacao(nova_empresa.email, token)

        return EmpresaOut.model_validate(nova_empresa)


    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email ou CNPJ já cadastrado")

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar empresa: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/pagar/{empresa_id}")
def gerar_link_pagamento(empresa_id: int, db: Session = Depends(banco_dados.get_db)):
    """
    Retorna o link de pagamento para o cliente escolher forma de pagamento.
    Se ainda não existir, cria o cliente e a cobrança no Asaas.
    """
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    if not empresa.pagamento_link:
        try:
            cliente_id = criar_cliente_asaas(empresa)
            pagamento_id, pagamento_status, pagamento_link = criar_link_pagamento_asaas(cliente_id, empresa)
            empresa.pagamento_id = pagamento_id
            empresa.pagamento_status = pagamento_status
            empresa.pagamento_link = pagamento_link
            db.commit()
            db.refresh(empresa)
        except Exception as e:
            logger.error(f"Erro ao gerar link de pagamento: {e}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Erro ao gerar link de pagamento")

    return {"pagamento_link": empresa.pagamento_link}
