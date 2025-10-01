from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.rmtpark_api.database.banco_dados import Base, engine
from src.rmtpark_api.api import auth, empresa, vaga, relatorio, mensalista

# Cria todas as tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RmtPark API")

# CORS
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://rmtpark-tcc-u856.vercel.app",
    "https://rmtpark-api.onrender.com",
]



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "https://rmtpark-tcc-u856.vercel.app",
        "https://rmtpark-bd.onrender.com",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(auth.router, prefix="/api/auth")
app.include_router(empresa.router, prefix="/api/empresa")
app.include_router(vaga.router, prefix="/api/vagas", tags=["vagas"])
app.include_router(relatorio.router, prefix="/api/relatorios", tags=["relatorios"])
app.include_router(mensalista.router, prefix="/api/mensalistas", tags=["mensalistas"])

@app.get("/")
def home():
    return {"status": "API RmtPark funcionando 🚀"}

# Executa local
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("src.rmtpark_api.main:app", host="0.0.0.0", port=port, reload=True)
