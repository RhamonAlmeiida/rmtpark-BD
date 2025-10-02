from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Pega URL do banco do .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Cria engine
engine = create_engine(DATABASE_URL)

# Base para os modelos
Base = declarative_base()

# Sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependência para FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
