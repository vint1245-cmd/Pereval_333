# app/routers/submitdata.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.submit_service import SubmitService
from app.schemas.pereval import PerevalOut

router = APIRouter(prefix="/submitData", tags=["submitData"])


def get_service(db: Session = Depends(get_db)) -> SubmitService:
    return SubmitService(db)


@router.get("/{pereval_id}", response_model=PerevalOut)
def get_submit_by_id(pereval_id: int, service: SubmitService = Depends(get_service)):
    """
    GET /submitData/{id}
    Возвращает одну запись Pereval по id с вложенными user, coords, level, images.
    """
    obj = service.get_pereval_by_id(pereval_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Pereval not found")
    return obj


@router.get("", response_model=List[PerevalOut])
def get_submits_by_email(
    user__email: str = Query(..., alias="user__email"),
    service: SubmitService = Depends(get_service),
):
    """
    GET /submitData?user__email=<email>
    Возвращает список записей Pereval, связанных с пользователем с указанным email.
    """
    results = service.get_perevals_by_user_email(user__email)
    return results
