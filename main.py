import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.rmtpark_api.api import auth, empresa, vaga, relatorio, mensalista, teste_email
from src.rmtpark_api.api import admin_routes
from src.rmtpark_api.database import modelos
from src.rmtpark_api.database.banco_dados import Base, engine


app = FastAPI(title="RmtPark API" ,version="1.0.0")

# Cria todas as tabelas no banco
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Erro ao criar tabelas no banco : {e}")

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
app.include_router(admin_routes.router, prefix="/api/admin")

@app.get("/")
def home():
    return {"status": "API RmtPark funcionando 🚀"}


# Execução local
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="127.0.0.1", port=port)
