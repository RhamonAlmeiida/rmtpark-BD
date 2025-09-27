import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.rmtpark_api.api import auth, empresa, vaga, relatorio
from src.rmtpark_api.database.banco_dados import Base, engine

# Cria todas as tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RmtPark API")

# CORS
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "https://rmtpark.netlify.app",
    "https://api.rmt-park.com"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api")
app.include_router(empresa.router, prefix="/api/empresa")
app.include_router(vaga.router, prefix="/api/vagas")
app.include_router(relatorio.router, prefix="/api/relatorios")

@app.get("/")
def home():
    return {"status": "API RmtPark funcionando 🚀"}

# Executa somente se rodar localmente
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # pega porta do Render ou usa 8000 local
    reload_env = os.environ.get("ENV", "local") == "local"  # só faz reload em dev
    uvicorn.run("src.rmtpark_api.main:app", host="0.0.0.0", port=port, reload=reload_env)
