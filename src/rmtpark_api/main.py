from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.rmtpark_api.api import auth, empresa, vaga
from src.rmtpark_api.database.banco_dados import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RmtPark API")




origins = [
    "http://localhost:4200",  # Angular
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(empresa.router, prefix="/api/empresa")
app.include_router(vaga.router, prefix="/api/vagas")

@app.get("/")
def home():
    return {"status": "API RmtPark funcionando 🚀"}
