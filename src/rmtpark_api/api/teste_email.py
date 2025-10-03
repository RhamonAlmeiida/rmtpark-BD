# src/rmtpark_api/api/test_email.py
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from ..utils.email_utils import enviar_email_confirmacao

router = APIRouter(tags=["test_email"])

class EmailRequest(BaseModel):
    email: str

@router.post("/teste-email")
async def teste_email(request_data: EmailRequest, request: Request):
    destinatario = request_data.email
    try:
        await enviar_email_confirmacao(destinatario, "teste123")
    except Exception as e:
        return {
            "args": dict(request.query_params),
            "headers": dict(request.headers),
            "url": str(request.url),
            "error": f"Erro ao enviar e-mail: {e}"
        }

    return {
        "args": dict(request.query_params),
        "headers": dict(request.headers),
        "url": str(request.url),
        "msg": f"E-mail de teste enviado para {destinatario}"
    }
