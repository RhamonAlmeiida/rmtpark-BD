from fastapi import APIRouter, Request
from pydantic import BaseModel
from ..utils.email_utils import enviar_email_confirmacao
import traceback

router = APIRouter(tags=["test_email"])

# ---------- Modelo de requisição ----------
class EmailRequest(BaseModel):
    email: str

# ---------- Endpoint de teste ----------
@router.post("/teste-email")
async def teste_email(request_data: EmailRequest, request: Request):
    destinatario = request_data.email
    debug_info = {
        "args": dict(request.query_params),
        "headers": dict(request.headers),
        "url": str(request.url),
        "destinatario": destinatario,
        "step": "iniciando"
    }

    try:
        debug_info["step"] = "enviando_email_confirmacao"
        print(f"[DEBUG] {debug_info}")

        await enviar_email_confirmacao(destinatario, "teste123")

        debug_info["step"] = "email_enviado_sucesso"
        print(f"[DEBUG] {debug_info}")

        return {
            **debug_info,
            "msg": f"E-mail de teste enviado para {destinatario}"
        }

    except Exception as e:
        debug_info["step"] = "erro_ao_enviar_email"
        debug_info["error"] = str(e)
        debug_info["traceback"] = traceback.format_exc()
        print(f"[ERROR] {debug_info}")

        return debug_info
