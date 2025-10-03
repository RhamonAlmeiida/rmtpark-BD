import os
from email.message import EmailMessage
import aiosmtplib

MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.office365.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "True") == "True"
FRONT_URL = os.getenv("FRONT_URL", "https://rmtpark-tcc-u856.vercel.app")


async def send_email(destinatario: str, assunto: str, html_content: str):
    msg = EmailMessage()
    msg["From"] = MAIL_FROM
    msg["To"] = destinatario
    msg["Subject"] = assunto
    msg.set_content(html_content, subtype="html")

    print(f"[INFO] Tentando enviar e-mail para: {destinatario}")
    print(f"[INFO] SMTP: {MAIL_SERVER}:{MAIL_PORT}, STARTTLS={MAIL_STARTTLS}")

    try:
        await aiosmtplib.send(
            msg,
            hostname=MAIL_SERVER,
            port=MAIL_PORT,
            start_tls=MAIL_STARTTLS,
            username=MAIL_USERNAME,
            password=MAIL_PASSWORD
        )
        print(f"[SUCCESS] E-mail enviado para {destinatario}")
    except Exception as e:
        print(f"[ERROR] Falha ao enviar e-mail para {destinatario}: {e}")
        raise e


async def enviar_email_confirmacao(destinatario: str, token: str):
    link = f"{FRONT_URL}/confirmar-email?token={token}"
    corpo = f"""
    <html>
    <body>
        <h2>Olá! 👋</h2>
        <p>Obrigado por se cadastrar no <strong>RmtPark</strong>.</p>
        <p><a href="{link}" style="background-color:#2E8B57;color:white;padding:10px 20px;text-decoration:none;">Confirmar e-mail</a></p>
    </body>
    </html>
    """
    await send_email(destinatario, "Confirme seu e-mail", corpo)


async def enviar_email_recuperacao(destinatario: str, token: str):
    link = f"{FRONT_URL}/redefinir-senha?token={token}"
    corpo = f"""
    <html>
    <body>
        <h2>Olá! 👋</h2>
        <p>Solicitação de redefinição de senha no <strong>RmtPark</strong>.</p>
        <p><a href="{link}" style="background-color:#FF6347;color:white;padding:10px 20px;text-decoration:none;">Redefinir senha</a></p>
    </body>
    </html>
    """
    await send_email(destinatario, "Recuperação de senha", corpo)
