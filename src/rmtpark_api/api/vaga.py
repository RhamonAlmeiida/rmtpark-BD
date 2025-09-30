from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import modelos
from ..database.banco_dados import get_db
from ..schemas import vaga as vaga_schema
from ..schemas.config import ConfigSchema
from ..utils.security import get_current_empresa

router = APIRouter(tags=["vagas"])


Vaga = modelos.Vaga
Relatorio = modelos.Relatorio
Configuracao = modelos.Configuracao

# ------------------- CRIAR VAGA -------------------
@router.post("/", response_model=vaga_schema.VagaResponse)
def criar_vaga(
    vaga: vaga_schema.VagaCreate,
    db: Session = Depends(get_db),
    empresa_logada: modelos.Empresa = Depends(get_current_empresa)
):
    nova_vaga = Vaga(
        placa=vaga.placa.upper(),
        tipo=vaga.tipo,
        data_hora=vaga.data_hora.replace(tzinfo=None) if vaga.data_hora else None,
        empresa_id=empresa_logada.id
    )
    db.add(nova_vaga)
    db.commit()
    db.refresh(nova_vaga)
    return nova_vaga


# ------------------- BUSCAR VAGA -------------------
@router.get("/{vaga_id}", response_model=vaga_schema.VagaResponse)
def buscar_vaga(
    vaga_id: int,
    db: Session = Depends(get_db),
    empresa_logada: modelos.Empresa = Depends(get_current_empresa)
):
    vaga = db.query(Vaga).filter(
        Vaga.id == vaga_id,
        Vaga.empresa_id == empresa_logada.id
    ).first()
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    return vaga


# ------------------- LISTAR VAGAS -------------------
@router.get("/", response_model=List[vaga_schema.VagaResponse])
def listar_vagas(
    db: Session = Depends(get_db),
    empresa_logada: modelos.Empresa = Depends(get_current_empresa)
):
    return db.query(Vaga).filter(
        Vaga.empresa_id == empresa_logada.id
    ).all()


# ------------------- DELETAR VAGA -------------------
@router.delete("/{vaga_id}")
def deletar_vaga(
    vaga_id: int,
    db: Session = Depends(get_db),
    empresa_logada: modelos.Empresa = Depends(get_current_empresa)
):
    vaga = db.query(Vaga).filter(
        Vaga.id == vaga_id,
        Vaga.empresa_id == empresa_logada.id
    ).first()
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")

    db.delete(vaga)
    db.commit()
    return {"detail": "Vaga removida com sucesso"}


# ------------------- REGISTRAR SAÍDA -------------------
@router.put("/{vaga_id}/saida", response_model=vaga_schema.VagaResponse)
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

    config = db.query(Configuracao).filter_by(empresa_id=empresa_logada.id).first()
    if not config:
        raise HTTPException(400, detail="Configurações não encontradas para esta empresa")

    # calcula saída
    saida = datetime.now()
    duracao = saida - vaga.data_hora
    minutos_totais = duracao.total_seconds() / 60

    # aplica arredondamento
    arred_min = config.arredondamento
    minutos_arred = ((minutos_totais + arred_min - 1) // arred_min) * arred_min
    horas = minutos_arred / 60
    duracao_str = str(timedelta(minutes=minutos_arred))

    # calcula valor
    if vaga.tipo == "Diarista":
        valor = config.valor_diaria if config.valor_diaria > 0 else round(horas * config.valor_hora, 2)
    elif vaga.tipo == "Mensalista":
        valor = config.valor_mensalista
    else:
        valor = round(horas * config.valor_hora, 2)

    vaga.data_hora_saida = saida
    vaga.duracao = duracao_str
    vaga.valor_pago = valor
    vaga.forma_pagamento = dados.formaPagamento or config.forma_pagamento
    vaga.status_pagamento = "Pago" if vaga.tipo == "Diarista" else "Mensalista"

    relatorio = Relatorio(
        placa=vaga.placa,
        tipo=vaga.tipo,
        data_hora_entrada=vaga.data_hora,
        data_hora_saida=saida,
        duracao=duracao_str,
        valor_pago=valor,
        forma_pagamento=vaga.forma_pagamento,
        status_pagamento=vaga.status_pagamento,
        empresa_id=vaga.empresa_id
    )

    db.add(relatorio)
    db.commit()
    db.refresh(relatorio)

    db.delete(vaga)
    db.commit()

    return relatorio


# ------------------- CONFIGURAÇÕES -------------------

@router.post("/configuracoes", response_model=ConfigSchema)
def salvar_configuracoes(
    dados: ConfigSchema,
    db: Session = Depends(get_db),
    empresa_logada: modelos.Empresa = Depends(get_current_empresa)
):
    config = db.query(Configuracao).filter_by(empresa_id=empresa_logada.id).first()
    if not config:
        config = Configuracao(empresa_id=empresa_logada.id)
        db.add(config)

    config.valor_hora = dados.valorHora
    config.valor_diaria = dados.valorDiaria
    config.valor_mensalista = dados.valorMensalista
    config.arredondamento = dados.arredondamento
    config.forma_pagamento = dados.formaPagamento

    db.commit()
    db.refresh(config)
    return config


@router.get("/configuracoes", response_model=ConfigSchema)
def obter_configuracoes(
    db: Session = Depends(get_db),
    empresa_logada: modelos.Empresa = Depends(get_current_empresa)
):
    config = db.query(Configuracao).filter_by(empresa_id=empresa_logada.id).first()
    if not config:
        raise HTTPException(404, "Configurações não encontradas")
    return config


