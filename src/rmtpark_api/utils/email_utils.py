import os
from email.message import EmailMessage
import aiosmtplib

# Variáveis de ambiente
MAIL_FROM = os.getenv("MAIL_FROM")
FRONT_URL = os.getenv("FRONT_URL", "https://api.rmtpark.com")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_STARTTLS = os.getenv("SMTP_STARTTLS", "True") == "True"

async def send_email(destinatario: str, assunto: str, html_content: str):
    msg = EmailMessage()
    msg["From"] = MAIL_FROM
    msg["To"] = destinatario
    msg["Subject"] = assunto
    msg.set_content(html_content, subtype="html")

    print(f"[INFO] Tentando enviar e-mail para: {destinatario}")
    print(f"[INFO] SMTP: {SMTP_HOST}:{SMTP_PORT}, STARTTLS={SMTP_STARTTLS}")

    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=SMTP_STARTTLS,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD
        )
        print(f"[SUCCESS] E-mail enviado para {destinatario}")
    except Exception as e:
        print(f"[ERROR] Falha ao enviar e-mail para {destinatario}: {e}")
        raise e

# E-mails de confirmação
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

# E-mails de recuperação de senha
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
