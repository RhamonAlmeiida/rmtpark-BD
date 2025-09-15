from sqlalchemy import Column, Integer, String, Boolean
from .banco_dados import Base

class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    empresa = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    telefone = Column(String(20), nullable=False)
    cnpj = Column(String(20), unique=True, nullable=False)
    senha = Column(String(255), nullable=False)  # será armazenada com hash
    email_confirmado = Column(Boolean, default=False)
