from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from dotenv import load_dotenv

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


async def enviar_email_confirmacao(email: str, link: str):
    message = MessageSchema(
        subject="Confirme seu e-mail - RmtPark",
        recipients=[email],
        body=f"""
        <h2>Bem-vindo ao RmtPark 🚗</h2>
        <p>Para ativar sua conta, confirme seu e-mail clicando no link abaixo:</p>
        <a href="{link}">👉 Confirmar e-mail</a>
        <p>Se você não fez este cadastro, ignore esta mensagem.</p>
        """,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)


async def enviar_email_recuperacao(email: str, link: str):
    message = MessageSchema(
        subject="Recuperação de senha - RmtPark",
        recipients=[email],
        body=f"""
        <h2>Recuperação de senha</h2>
        <p>Recebemos uma solicitação para redefinir sua senha.</p>
        <a href="{link}">👉 Redefinir senha</a>
        <p>Se você não solicitou esta ação, ignore esta mensagem.</p>
        """,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
