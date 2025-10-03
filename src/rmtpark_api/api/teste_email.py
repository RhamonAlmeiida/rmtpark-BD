from fastapi import APIRouter
from pydantic import BaseModel
from ..utils.email_utils import enviar_email_confirmacao
import asyncio

router = APIRouter(tags=["test_email"])

class EmailRequest(BaseModel):
    email: str

@router.post("/teste-email")
async def teste_email(request_data: EmailRequest):
    destinatario = request_data.email
    try:
        await enviar_email_confirmacao(destinatario, token="teste123")
        return {"msg": f"E-mail de teste enviado para {destinatario}"}
    except Exception as e:
        return {"error": str(e)}
