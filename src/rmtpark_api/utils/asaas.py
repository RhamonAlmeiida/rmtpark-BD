import requests, os
from fastapi import HTTPException
from ..database.modelos import Empresa
from datetime import datetime, timedelta


# === CONFIGURAÇÃO ===
ASAAS_API_KEY = os.getenv("ASAAS_API_KEY")  # pega do .env
ASAAS_API_URL = "https://sandbox.asaas.com/api/v3/"

HEADERS = {
    "access_token": ASAAS_API_KEY,
    "Content-Type": "application/json"
}

def criar_cliente_asaas(empresa: dict):
    """
    Cria um cliente no Asaas Sandbox.
    empresa: dict com chaves 'nome', 'email', 'telefone', 'cpfCnpj'
    """
    url = ASAAS_API_URL + "customers"
    payload = {
        "name": empresa["nome"],
        "email": empresa["email"],
        "phone": empresa["telefone"],
        "cpfCnpj": empresa["cnpj"],
        "externalReference": str(empresa.get("id", ""))  # opcional, para vincular ao seu sistema
    }

    response = requests.post(url, json=payload, headers=HEADERS)
    data = response.json()

    if response.status_code != 200 and response.status_code != 201:
        raise HTTPException(status_code=500, detail=f"Erro ao criar cliente Asaas: {data}")

    return data["id"]  # retorna o ID do cliente no Asaas

def criar_link_pagamento_asaas(cliente_id, empresa: Empresa, dias_vencimento=5):
    valor = float(empresa.plano_preco.replace("R$ ", "").replace("/mês", "").replace(",", "."))
    due_date = (datetime.now() + timedelta(days=dias_vencimento)).strftime("%Y-%m-%d")
    payload = {
        "customer": cliente_id,
        "billingType": "CREDIT_CARD",
        "value": valor,
        "dueDate": due_date,
        "description": f"Assinatura do plano {empresa.plano_titulo}",
        "externalReference": str(empresa.id),
        "notificationUrl": "https://seusite.com/notificacao-pagamento",
        "billingTypeOptions": ["BOLETO", "CREDIT_CARD", "PIX"]
    }
    response = requests.post(f"{ASAAS_API_URL}/payments", headers=HEADERS, json=payload)
    data = response.json()
    if response.status_code not in [200, 201]:
        raise HTTPException(status_code=500, detail=f"Erro Asaas: {data}")

    # Retorna ID da cobrança e link do checkout (sandbox pode gerar link diferente)
    checkout_link = f"https://sandbox.asaas.com/payment/{data['id']}"
    return data.get("id"), data.get("status"), checkout_link
