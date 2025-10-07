# src/rmtpark_api/database/modelos.py
from sqlalchemy import (
    Column, Integer, String, Boolean, ARRAY, Float, ForeignKey, DateTime, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    telefone = Column(String(20), nullable=False)
    cnpj = Column(String(20), unique=True, nullable=False)
    senha = Column(String(255), nullable=False)
    email_confirmado = Column(Boolean, default=False)

    # Campos do plano
    plano_titulo = Column(String(100), nullable=False)
    plano_preco = Column(String(20), nullable=False)
    plano_recursos = Column(ARRAY(String))
    plano_destaque = Column(Boolean, default=False)

    # Campos do pagamento
    pagamento_id = Column(String, nullable=True)
    pagamento_status = Column(String, nullable=True)
    pagamento_link = Column(String, nullable=True)

    # -------------------------------
    # Relacionamentos
    # -------------------------------
    vagas = relationship(
        "Vaga",
        back_populates="empresa",
        cascade="all, delete-orphan"
    )
    relatorios = relationship(
        "Relatorio",
        back_populates="empresa",
        cascade="all, delete-orphan"
    )
    configuracao = relationship(
        "Configuracao",
        uselist=False,
        back_populates="empresa",
        cascade="all, delete-orphan"
    )
    mensalistas = relationship(
        "Mensalista",
        back_populates="empresa",
        cascade="all, delete-orphan"
    )

    # -------------------------------
    # Propriedade compatível com Pydantic
    # -------------------------------
    @property
    def plano(self):
        return {
            "titulo": self.plano_titulo,
            "preco": self.plano_preco,
            "recursos": self.plano_recursos,
            "destaque": self.plano_destaque
        }

    @plano.setter
    def plano(self, value: dict):
        self.plano_titulo = value.get("titulo", "")
        self.plano_preco = value.get("preco", "")
        self.plano_recursos = value.get("recursos", [])
        self.plano_destaque = value.get("destaque", False)


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
    __table_args__ = (
        UniqueConstraint('placa', 'empresa_id', name='mensalistas_placa_empresa_unique'),
    )

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    placa = Column(String(20), nullable=False)
    veiculo = Column(String(50), nullable=False)
    cor = Column(String(30), nullable=False)
    cpf = Column(String(20), nullable=False)
    validade = Column(DateTime, nullable=False)
    status = Column(String(20), default="ativo")
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)

    empresa = relationship("Empresa", back_populates="mensalistas")
