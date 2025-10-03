import os
from email.message import EmailMessage
import aiosmtplib

# -----------------------
# Configurações de e-mail
# -----------------------
MAIL_FROM = os.getenv("SMTP_USERNAME", os.getenv("MAIL_FROM"))
MAIL_USERNAME = os.getenv("SMTP_USERNAME", MAIL_FROM)
MAIL_PASSWORD = os.getenv("SMTP_PASSWORD", os.getenv("MAIL_PASSWORD"))
MAIL_SERVER = os.getenv("SMTP_HOST", os.getenv("MAIL_SERVER", "smtp.office365.com"))
MAIL_PORT = int(os.getenv("SMTP_PORT", 587))
MAIL_STARTTLS = os.getenv("SMTP_STARTTLS", "True").lower() in ["true", "1", "yes"]
FRONT_URL = os.getenv("FRONT_URL", "http://localhost:4200")


# -----------------------
# Função genérica de envio
# -----------------------
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
            password=MAIL_PASSWORD,
            timeout=30  # aumenta timeout para evitar erros de conexão
        )
        print(f"[SUCCESS] E-mail enviado para {destinatario}")
    except Exception as e:
        print(f"[ERROR] Falha ao enviar e-mail para {destinatario}: {e}")
        raise e


# -----------------------
# E-mail de confirmação
# -----------------------
async def enviar_email_confirmacao(destinatario: str, token: str):
    link = f"{FRONT_URL}/confirmar-email?token={token}"
    corpo = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #2E8B57;">Olá! 👋</h2>
        <p>Obrigado por se cadastrar no <strong>RmtPark</strong>.</p>
        <p style="text-align:center;">
            <a href="{link}" style="background-color:#2E8B57;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">Confirmar e-mail</a>
        </p>
        <p>Se você não se cadastrou, apenas ignore este e-mail.</p>
        <hr>
        <p style="font-size:12px;color:#777;">RmtPark &copy; 2025</p>
    </body>
    </html>
    """
    await send_email(destinatario, "Confirme seu e-mail", corpo)


# -----------------------
# E-mail de recuperação de senha
# -----------------------
async def enviar_email_recuperacao(destinatario: str, token: str):
    link = f"{FRONT_URL}/redefinir-senha?token={token}"
    corpo = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color:#FF6347;">Olá! 👋</h2>
        <p>Recebemos uma solicitação para redefinir sua senha no <strong>RmtPark</strong>.</p>
        <p style="text-align:center;">
            <a href="{link}" style="background-color:#FF6347;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">Redefinir senha</a>
        </p>
        <p>Se você não solicitou a alteração, apenas ignore este e-mail.</p>
        <hr>
        <p style="font-size:12px;color:#777;">RmtPark &copy; 2025</p>
    </body>
    </html>
    """
    await send_email(destinatario, "Recuperação de senha", corpo)
