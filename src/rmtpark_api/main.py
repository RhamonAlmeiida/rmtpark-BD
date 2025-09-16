from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.rmtpark_api.api import auth, empresa
from src.rmtpark_api.database.banco_dados import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RmtPark API")

# Incluindo rotas
app.include_router(auth.router)
app.include_router(empresa.router)

# Configuração do CORS
origins = [
    "http://localhost:4200",  # Angular
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # permite requisições só dessas origens
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Headers customizados
)

@app.get("/")
def home():
    return {"status": "API RmtPark funcionando 🚀"}
