# src/rmtpark_api/utils/email_utils.py
from dotenv import load_dotenv
load_dotenv()  # Carrega o .env antes de pegar as variáveis

import os
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from typing import Optional

# -----------------------
# Configuração do FastMail
# -----------------------
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

# URL do frontend
FRONT_URL = os.getenv("FRONT_URL", "http://localhost:4200")

# -----------------------
# Função para montar link de confirmação
# -----------------------
def montar_link_confirmacao(token: str) -> str:
    """
    Monta o link completo de confirmação de e-mail
    """
    return f"{FRONT_URL}/confirmar-email?token={token}"

# -----------------------
# Função para enviar e-mail de confirmação
# -----------------------
async def enviar_email_confirmacao(destinatario: str, link: str):
    """
    Envia e-mail de confirmação de cadastro
    """
    assunto = "Confirme seu e-mail"
    corpo = f"""
    Olá! 👋<br><br>
    Obrigado por se cadastrar no RmtPark.<br>
    Por favor, confirme seu e-mail clicando no link abaixo:<br><br>
    <a href="{link}">Confirmar e-mail</a><br><br>
    Se você não se cadastrou, apenas ignore este e-mail.
    """
    message = MessageSchema(
        subject=assunto,
        recipients=[destinatario],
        body=corpo,
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message)

# -----------------------
# Função para enviar e-mail de recuperação de senha
# -----------------------
async def enviar_email_recuperacao(destinatario: str, token: str):
    """
    Envia e-mail de recuperação de senha
    """
    link = f"{FRONT_URL}/redefinir-senha?token={token}"
    assunto = "Recuperação de senha"
    corpo = f"""
    Olá! 👋<br><br>
    Você solicitou a recuperação de senha no RmtPark.<br>
    Clique no link abaixo para redefinir sua senha:<br><br>
    <a href="{link}">Redefinir senha</a><br><br>
    Se você não solicitou, apenas ignore este e-mail.
    """
    message = MessageSchema(
        subject=assunto,
        recipients=[destinatario],
        body=corpo,
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message)
