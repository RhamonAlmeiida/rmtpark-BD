from fastapi import FastAPI
from src.rmtpark_api.api import empresa
from src.rmtpark_api.database.banco_dados import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(empresa.router)
