import os
from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig

# Configuração do FastMail com SendGrid
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),  # normalmente "apikey" para SendGrid
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),  # sua chave API SendGrid
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    USE_CREDENTIALS=True,
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True") == "True",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False") == "True",
)

FRONT_URL = os.getenv("FRONT_URL")  # URL do front-end

async def enviar_email_confirmacao(destinatario: str, token: str):
    link = f"{FRONT_URL}/confirmar-email?token={token}"
    assunto = "Confirme seu e-mail"
    corpo = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #2E8B57;">Olá! 👋</h2>
        <p>Obrigado por se cadastrar no <strong>RmtPark</strong>.</p>
        <p>Por favor, confirme seu e-mail clicando no botão abaixo:</p>
        <p style="text-align:center;">
            <a href="{link}" style="background-color:#2E8B57;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">Confirmar e-mail</a>
        </p>
        <p>Se você não se cadastrou, apenas ignore este e-mail.</p>
        <hr>
        <p style="font-size:12px;color:#777;">RmtPark &copy; 2025</p>
    </body>
    </html>
    """
    message = MessageSchema(
        subject=assunto,
        recipients=[destinatario],
        body=corpo,
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message)

async def enviar_email_recuperacao(destinatario: str, token: str):
    link = f"{FRONT_URL}/redefinir-senha?token={token}"
    assunto = "Recuperação de senha"
    corpo = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color:#FF6347;">Olá! 👋</h2>
        <p>Recebemos uma solicitação para redefinir sua senha no <strong>RmtPark</strong>.</p>
        <p>Clique no botão abaixo para redefinir sua senha:</p>
        <p style="text-align:center;">
            <a href="{link}" style="background-color:#FF6347;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">Redefinir senha</a>
        </p>
        <p>Se você não solicitou a alteração, apenas ignore este e-mail.</p>
        <hr>
        <p style="font-size:12px;color:#777;">RmtPark &copy; 2025</p>
    </body>
    </html>
    """
    message = MessageSchema(
        subject=assunto,
        recipients=[destinatario],
        body=corpo,
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message)

def montar_link_confirmacao(token: str) -> str:
    from src.rmtpark_api.config import FRONT_URL
    return f"{FRONT_URL}/confirmar-email?token={token}"
