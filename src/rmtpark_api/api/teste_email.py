# src/rmtpark_api/api/test_email.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import banco_dados
from ..database.modelos import Empresa

router = APIRouter(tags=["test_email"])

@router.post("/ativar-todos-usuarios-teste")
def ativar_todos_usuarios(db: Session = Depends(banco_dados.get_db)):
    # Atualiza todos os registros para email_confirmado = True
    db.query(Empresa).update({Empresa.email_confirmado: True})
    db.commit()
    return {"msg": "Todos os usuários ativados para teste!"}
