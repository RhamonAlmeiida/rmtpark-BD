from datetime import datetime
import pytz

TZ_SP = pytz.timezone("America/Sao_Paulo")

def agora_sp() -> datetime:
    """Retorna o horário atual com fuso de São Paulo (UTC−3)"""
    return datetime.now(TZ_SP)