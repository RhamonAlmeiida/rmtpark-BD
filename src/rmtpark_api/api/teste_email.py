# src/rmtpark_api/api/test_email.py
from fastapi import APIRouter
from ..utils.email_utils import enviar_email_confirmacao
from fastapi import HTTPException

router = APIRouter(tags=["test_email"])

@router.get("/teste-email")
async def teste_email():
    try:
        # Troque para o seu e-mail real para teste
        destinatario = "seuemail@dominio.com"
        link = "https://example.com/confirmar-email?token=teste123"
        await enviar_email_confirmacao(destinatario, link)
        return {"msg": f"E-mail de teste enviado para {destinatario}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar e-mail: {e}")
