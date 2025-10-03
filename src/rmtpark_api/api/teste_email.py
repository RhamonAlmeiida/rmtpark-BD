# src/rmtpark_api/api/test_email.py
from fastapi import APIRouter, HTTPException
from ..utils.email_utils import enviar_email_confirmacao

router = APIRouter(tags=["test_email"])


@router.get("/teste-email")
async def teste_email():
    try:
        # Coloque seu e-mail de destino aqui
        destinatario = "rmtpark.estacionamento@gmail.com"
        link = "https://example.com/confirmar-email?token=teste123"

        await enviar_email_confirmacao(destinatario, link)
        return {"msg": f"E-mail de teste enviado para {destinatario}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar e-mail: {e}")
