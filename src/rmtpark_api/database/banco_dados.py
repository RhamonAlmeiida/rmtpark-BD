from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()  # Carrega .env automaticamente

# Pega do .env ou usa fallback SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rmtpark.db")

engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Função para gerar sessão de banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
