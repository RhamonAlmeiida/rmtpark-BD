# src/rmtpark_api/utils/email_utils.py
import os
from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig

# Configurações do SendGrid via SMTP
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "apikey"),   # sempre "apikey" no SendGrid
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),             # sua API Key do SendGrid
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.sendgrid.net"),
    USE_CREDENTIALS=True,
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True") == "True",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False") == "True",
)

FRONT_URL = os.getenv("FRONT_URL")  # pega direto das env

# ---------------------------
# E-mail de confirmação
# ---------------------------
async def enviar_email_confirmacao(destinatario: str, token: str):
    link = f"{FRONT_URL}/confirmar-email?token={token}"
    corpo = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #2E8B57;">Olá 👋</h2>
        <p>Obrigado por se cadastrar no <strong>RmtPark</strong>.</p>
        <p>Clique no botão abaixo para confirmar seu e-mail:</p>
        <p style="text-align:center;">
            <a href="{link}" 
               style="background-color:#2E8B57;color:white;padding:10px 20px;
                      text-decoration:none;border-radius:5px;">Confirmar e-mail</a>
        </p>
        <p>Se você não se cadastrou, apenas ignore este e-mail.</p>
    </body>
    </html>
    """
    message = MessageSchema(
        subject="Confirme seu e-mail",
        recipients=[destinatario],
        body=corpo,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(message)

# ---------------------------
# E-mail de recuperação
# ---------------------------
async def enviar_email_recuperacao(destinatario: str, token: str):
    link = f"{FRONT_URL}/redefinir-senha?token={token}"
    corpo = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color:#FF6347;">Recuperar senha 🔑</h2>
        <p>Recebemos um pedido para redefinir sua senha no <strong>RmtPark</strong>.</p>
        <p>Clique no botão abaixo para criar uma nova senha:</p>
        <p style="text-align:center;">
            <a href="{link}" 
               style="background-color:#FF6347;color:white;padding:10px 20px;
                      text-decoration:none;border-radius:5px;">Redefinir senha</a>
        </p>
        <p>Se você não pediu isso, ignore este e-mail.</p>
    </body>
    </html>
    """
    message = MessageSchema(
        subject="Recuperação de senha",
        recipients=[destinatario],
        body=corpo,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(message)
