import os
import httpx

# -----------------------
# Configurações diretas
# -----------------------
SENDGRID_API_KEY = os.getenv("MAIL_PASSWORD")
# exemplo: "SG.xxxxx"
SENDGRID_FROM = "seuemail@dominio.com"
FRONT_URL = "http://localhost:4200"  # ou a URL do seu front

# -----------------------
# Função auxiliar
# -----------------------
async def send_email(destinatario: str, assunto: str, html_content: str):
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "personalizations": [{
            "to": [{"email": destinatario}],
            "subject": assunto
        }],
        "from": {"email": SENDGRID_FROM},
        "content": [{
            "type": "text/html",
            "value": html_content
        }]
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=data)
        if resp.status_code >= 400:
            raise Exception(f"Erro SendGrid: {resp.status_code} - {resp.text}")

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
    await send_email(destinatario, "Recuperação de senha", corpo)
