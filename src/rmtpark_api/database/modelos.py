from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime  # <-- CORRETO
from .banco_dados import Base

Base = declarative_base()


class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    telefone = Column(String(20), nullable=False)
    cnpj = Column(String(20), unique=True, nullable=False)
    senha = Column(String(255), nullable=False)  # será armazenada com hash
    email_confirmado = Column(Boolean, default=False)
    api_token = Column(String(255), unique=True, index=True, nullable=True)  # Token simples

    vagas = relationship("Vaga" , back_populates="empresa")


class Vaga(Base):
    __tablename__ = "vagas"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(7), nullable=False , index=True)
    tipo = Column(String(10), nullable=False)
    data_hora = Column(DateTime, default=datetime.utcnow)

    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)

    empresa = relationship("Empresa", back_populates="vagas")