from fastapi import FastAPI
from .api import empresa

app = FastAPI()

app.include_router(empresa.router)

@app.get("/")
def home():
    return {"status": "API RmtPark funcionando 🚀"}
