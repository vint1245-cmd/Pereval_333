from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.pereval import PerevalCreate
from app.repositories.submit_data import (
    create_pereval_repo,
    get_pereval_by_id_repo,
    update_pereval_repo
)

def create_pereval(db: Session, payload: PerevalCreate):
    pereval = create_pereval_repo(db, payload)
    return pereval

def get_pereval(db: Session, pereval_id: int):
    pereval = get_pereval_by_id_repo(db, pereval_id)
    if not pereval:
        raise HTTPException(status_code=404, detail="Pereval not found")
    return pereval
    
def update_pereval(db: Session, pereval_id: int, payload):
    pereval = get_pereval_by_id_repo(db, pereval_id)
    if not pereval:
        return {"state": 0, "message": "Перевал не найден"}

    if pereval.status != "new":
        return {"state": 0, "message": "Редактирование запрещено: статус != new"}

    # Нельзя менять пользователя
    if payload.user.email != pereval.user.email:
        return {"state": 0, "message": "Нельзя изменять данные пользователя"}

    updated = update_pereval_repo(db, pereval, payload)

    return {"state": 1, "message": "Запись успешно обновлена"}
    
