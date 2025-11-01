# src/rmtpark_api/api/vaga.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import modelos
from ..database.banco_dados import get_db
from ..schemas import vaga as vaga_schema
from ..schemas.vaga import ConfigSchema
from ..utils.security import get_current_empresa

router = APIRouter(tags=["vagas"])

Vaga = modelos.Vaga
Relatorio = modelos.Relatorio
Configuracao = modelos.Configuracao

# ------------------- PING -------------------
@router.get("/ping")
def ping():
    return {"status": "pong"}

# ------------------- LISTAR VAGAS -------------------
@router.get("/", response_model=List[vaga_schema.VagaResponse])
def listar_vagas(
    db: Session = Depends(get_db),
    empresa_logada: modelos.Empresa = Depends(get_current_empresa)
):
    vagas = db.query(Vaga).filter(Vaga.empresa_id == empresa_logada.id).all()
    return vagas

# ------------------- CRIAR VAGA -------------------
@router.post("/", response_model=vaga_schema.VagaResponse)
def criar_vaga(
    vaga: vaga_schema.VagaCreate,
    db: Session = Depends(get_db),
    empresa_logada: modelos.Empresa = Depends(get_current_empresa)
):
    # --- Verifica limite de vagas ativas conforme o plano ---
    plano = empresa_logada.plano_titulo.lower()
    limite = None

    if "basic" in plano:
        limite = 50
    elif "profissional" in plano:
        limite = 150
    elif "premium" in plano:
        limite = None  # ilimitado

    # Conta quantas vagas estão ativas (sem saída)
    vagas_ativas = db.query(Vaga).filter(
        Vaga.empresa_id == empresa_logada.id,
        Vaga.data_hora_saida.is_(None)
    ).count()

    # Se houver limite e ele for atingido, bloqueia nova criação
    if limite is not None and vagas_ativas >= limite:
        raise HTTPException(
            status_code=403,
            detail=f"Limite de {limite} vagas ativas atingido para o plano {empresa_logada.plano_titulo}."
        )

    data_hora = vaga.data_hora or datetime.now()
    nova_vaga = Vaga(
        placa=vaga.placa.upper(),
        tipo=vaga.tipo,
        data_hora=data_hora,
        empresa_id=empresa_logada.id
    )
    db.add(nova_vaga)
    db.commit()
    db.refresh(nova_vaga)
    return nova_vaga


# ------------------- REGISTRAR SAÍDA -------------------
@router.put("/{vaga_id}/saida")
def registrar_saida(
        vaga_id: int,
        dados: vaga_schema.VagaSaidaSchema,
        db: Session = Depends(get_db),
        empresa_logada: modelos.Empresa = Depends(get_current_empresa)
):
    vaga = db.query(Vaga).filter(
        Vaga.id == vaga_id,
        Vaga.empresa_id == empresa_logada.id
    ).first()

    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")

    config: Configuracao = db.query(Configuracao).filter_by(empresa_id=empresa_logada.id).first()
    if not config:
        raise HTTPException(status_code=400, detail="Configurações não encontradas")

    saida: datetime = dados.saida or datetime.now()
    duracao: timedelta = saida - vaga.data_hora
    minutos_totais = duracao.total_seconds() / 60
    arred_min = config.arredondamento or 1
    minutos_arred = ((minutos_totais + arred_min - 1) // arred_min) * arred_min
    duracao_str = str(timedelta(minutes=minutos_arred))
    horas = minutos_arred / 60

    if vaga.tipo.lower() == "diarista":
        valor = config.valor_diaria if config.valor_diaria > 0 else round(horas * config.valor_hora, 2)
    elif vaga.tipo.lower() == "mensalista":
        valor = config.valor_mensalista
    else:
        valor = round(horas * config.valor_hora, 2)

    forma_pagamento = dados.formaPagamento or config.forma_pagamento

    vaga.data_hora_saida = saida
    vaga.duracao = duracao_str
    vaga.valor_pago = valor
    vaga.forma_pagamento = forma_pagamento
    vaga.status_pagamento = "Pago" if vaga.tipo.lower() == "diarista" else "Mensalista"

    relatorio = Relatorio(
        placa=vaga.placa,
        tipo=vaga.tipo,
        data_hora_entrada=vaga.data_hora,
        data_hora_saida=saida,
        duracao=duracao_str,
        valor_pago=valor,
        forma_pagamento=forma_pagamento,
        status_pagamento=vaga.status_pagamento,
        empresa_id=vaga.empresa_id
    )

    db.add(relatorio)
    db.delete(vaga)
    db.commit()

    # Retorna apenas o sucesso e o ID do relatório
    return {
        "success": True,
        "mensagem": "Saída registrada com sucesso",
        "relatorio_id": relatorio.id
    }
# ------------------- CONFIGURAÇÕES -------------------
@router.post("/configuracoes", response_model=ConfigSchema)
def salvar_configuracoes(
    dados: ConfigSchema,
    db: Session = Depends(get_db),
    empresa_logada: modelos.Empresa = Depends(get_current_empresa)
):
    config: Optional[Configuracao] = db.query(Configuracao).filter_by(empresa_id=empresa_logada.id).first()
    if not config:
        config = Configuracao(empresa_id=empresa_logada.id)
        db.add(config)

    # Usando snake_case do Pydantic
    config.valor_hora = dados.valor_hora
    config.valor_diaria = dados.valor_diaria
    config.valor_mensalista = dados.valor_mensalista
    config.arredondamento = dados.arredondamento
    config.forma_pagamento = dados.forma_pagamento

    db.commit()
    db.refresh(config)
    return config

@router.get("/configuracoes", response_model=ConfigSchema)
def obter_configuracoes(
    db: Session = Depends(get_db),
    empresa_logada: modelos.Empresa = Depends(get_current_empresa)
):
    config: Optional[Configuracao] = db.query(Configuracao).filter_by(empresa_id=empresa_logada.id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configurações não encontradas")
    return config
