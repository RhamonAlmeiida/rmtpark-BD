from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .banco_dados import Base

class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    telefone = Column(String(20), nullable=False)
    cnpj = Column(String(20), unique=True, nullable=False)
    senha = Column(String(255), nullable=False)
    email_confirmado = Column(Boolean, default=False)
    api_token = Column(String(255), unique=True, index=True, nullable=True)

    vagas = relationship("Vaga", back_populates="empresa")
    relatorios = relationship("Relatorio", back_populates="empresa")


class Vaga(Base):
    __tablename__ = "vagas"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(7), nullable=False, index=True)
    tipo = Column(String(10), nullable=False)

    # hora de entrada automática
    data_hora = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # hora de saída preenchida na saída do veículo
    data_hora_saida = Column(DateTime(timezone=True), nullable=True)

    duracao = Column(String(20), nullable=True)
    valor = Column(Float, nullable=True)
    forma_pagamento = Column(String(20), nullable=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    empresa = relationship("Empresa", back_populates="vagas")


class Relatorio(Base):
    __tablename__ = "relatorios"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(10), nullable=False)
    tipo = Column(String(20), nullable=False)
    data_hora_entrada = Column(DateTime, nullable=False)
    data_hora_saida = Column(DateTime, nullable=False)
    duracao = Column(String(20), nullable=False)
    valor_pago = Column(Float, nullable=False)
    forma_pagamento = Column(String(20), nullable=False)
    status_pagamento = Column(String(20), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)

    empresa = relationship("Empresa", back_populates="relatorios")
