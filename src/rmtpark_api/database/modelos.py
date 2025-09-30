from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .banco_dados import Base


# ------------------ EMPRESA ------------------
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

    # Relacionamentos
    vagas = relationship("Vaga", back_populates="empresa", cascade="all, delete-orphan")
    relatorios = relationship("Relatorio", back_populates="empresa", cascade="all, delete-orphan")
    configuracao = relationship("Configuracao", uselist=False, back_populates="empresa")


# ------------------ VAGA ------------------
class Vaga(Base):
    __tablename__ = "vagas"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(10), nullable=False, index=True)
    tipo = Column(String(20), nullable=False)

    # entrada automática
    data_hora = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # saída preenchida no checkout
    data_hora_saida = Column(DateTime(timezone=True), nullable=True)

    duracao = Column(String(50), nullable=True)
    valor_pago = Column(Float, nullable=True)
    forma_pagamento = Column(String(20), nullable=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    empresa = relationship("Empresa", back_populates="vagas")


# ------------------ RELATÓRIO ------------------
class Relatorio(Base):
    __tablename__ = "relatorios"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(20), nullable=False)
    tipo = Column(String(20), nullable=False)
    data_hora_entrada = Column(DateTime, nullable=False)
    data_hora_saida = Column(DateTime, nullable=False)
    duracao = Column(String(50), nullable=False)
    valor_pago = Column(Float, nullable=False)
    forma_pagamento = Column(String(20), nullable=True)   # pode ser nulo
    status_pagamento = Column(String(20), nullable=False)

    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    empresa = relationship("Empresa", back_populates="relatorios")


# ------------------ CONFIGURAÇÃO ------------------
class Configuracao(Base):
    __tablename__ = "configuracoes"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), unique=True)

    valor_hora = Column(Float, default=10.0)
    valor_diaria = Column(Float, default=0.0)
    valor_mensalista = Column(Float, default=0.0)
    arredondamento = Column(Integer, default=15)  # minutos
    forma_pagamento = Column(String(20), default="Pix")

    empresa = relationship("Empresa", back_populates="configuracao")


# ------------------ MENSALISTA ------------------
class Mensalista(Base):
    __tablename__ = "mensalistas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    placa = Column(String, unique=True, nullable=False)
    veiculo = Column(String, nullable=False)
    cor = Column(String, nullable=True)
    cpf = Column(String, nullable=True)
    validade = Column(Date, nullable=False)
    status = Column(String, nullable=False)
