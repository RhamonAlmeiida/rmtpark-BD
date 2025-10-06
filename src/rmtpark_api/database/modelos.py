from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Date
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

    vagas = relationship("Vaga", back_populates="empresa", cascade="all, delete-orphan")
    relatorios = relationship("Relatorio", back_populates="empresa", cascade="all, delete-orphan")
    configuracao = relationship("Configuracao", uselist=False, back_populates="empresa")
    mensalistas = relationship("Mensalista", back_populates="empresa")


class Vaga(Base):
    __tablename__ = "vagas"
    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(10), nullable=False)
    tipo = Column(String(20), nullable=False)
    data_hora = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    data_hora_saida = Column(DateTime(timezone=True), nullable=True)
    duracao = Column(String(50), nullable=True)
    valor_pago = Column(Float, nullable=True)
    forma_pagamento = Column(String(20), nullable=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    empresa = relationship("Empresa", back_populates="vagas")

class Relatorio(Base):
    __tablename__ = "relatorios"
    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(20), nullable=False)
    tipo = Column(String(20), nullable=False)
    data_hora_entrada = Column(DateTime, nullable=False)
    data_hora_saida = Column(DateTime, nullable=False)
    duracao = Column(String(50), nullable=False)
    valor_pago = Column(Float, nullable=False)
    forma_pagamento = Column(String(20), nullable=True)
    status_pagamento = Column(String(20), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    empresa = relationship("Empresa", back_populates="relatorios")

class Configuracao(Base):
    __tablename__ = "configuracoes"
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), unique=True)
    valor_hora = Column(Float, default=10.0)
    valor_diaria = Column(Float, default=0.0)
    valor_mensalista = Column(Float, default=0.0)
    arredondamento = Column(Integer, default=15)
    forma_pagamento = Column(String(20), default="Pix")
    empresa = relationship("Empresa", back_populates="configuracao")

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


    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    empresa = relationship("Empresa", back_populates="mensalistas")