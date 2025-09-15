from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from src.rmtpark_api.database.modelos import Empresa
from src.rmtpark_api.api.auth import get_db, verificar_senha, criar_token_acesso, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.email == form_data.username).first()
    if not empresa or not verificar_senha(form_data.password, empresa.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = criar_token_acesso(data={"sub": empresa.email}, expires_delta=token_expires)

    return {"access_token": access_token, "token_type": "bearer"}
