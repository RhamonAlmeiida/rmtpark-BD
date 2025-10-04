from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.rmtpark_api.database.banco_dados import Base, engine
from src.rmtpark_api.api import auth, empresa, vaga, relatorio, mensalista, teste_email
import os

app = FastAPI(title="RmtPark API")

# Cria todas as tabelas no banco
Base.metadata.create_all(bind=engine)

# CORS
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "https://rmtpark-tcc-u856.vercel.app",
    "https://rmtpark-bd.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(auth.router, prefix="/api/auth")
app.include_router(empresa.router, prefix="/api/empresa")
app.include_router(vaga.router, prefix="/api/vagas")
app.include_router(relatorio.router, prefix="/api/relatorios", tags=["relatorios"])
app.include_router(mensalista.router, prefix="/api/mensalistas", tags=["mensalistas"])
app.include_router(teste_email.router, prefix="/api")

@app.get("/")
def home():
    return {"status": "API RmtPark funcionando 🚀"}

# Executa apenas se rodar localmente
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render usa a variável PORT
    import uvicorn
    uvicorn.run("src.rmtpark_api.main:app", host="0.0.0.0", port=port)
