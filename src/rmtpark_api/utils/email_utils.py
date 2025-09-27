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

async def enviar_email_confirmacao(email: str, token: str):
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:4200")
    link = f"{frontend_url}/confirmar-email?token={token}"
    message = MessageSchema(
        subject="Confirme seu e-mail - RmtPark",
        recipients=[email],
        body=f'<h2>Bem-vindo!</h2><p>Confirme seu e-mail: <a href="{link}">Confirmar</a></p>',
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)




async def enviar_email_recuperacao(email: str, token: str):
    """
    Envia e-mail de recuperação de senha para o usuário.
    O link aponta para o front-end em produção.
    """
    frontend_url = os.getenv("FRONTEND_URL", "https://rmtpark-tcc-u856.vercel.app")
    link = f"{frontend_url}/redefinir-senha?token={token}"

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


