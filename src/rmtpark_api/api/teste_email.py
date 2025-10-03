# src/rmtpark_api/api/test_email.py
from fastapi import APIRouter, HTTPException
from ..utils.email_utils import enviar_email_confirmacao

router = APIRouter(tags=["test_email"])


@router.get("/teste-email")
async def teste_email():
    try:
        destinatario = "seuemail@dominio.com"
        await enviar_email_confirmacao(destinatario, "teste123")
        return {"msg": f"E-mail de teste enviado para {destinatario}"}
    except Exception as e:
        return {"detail": f"Erro ao enviar e-mail: {e}"}
