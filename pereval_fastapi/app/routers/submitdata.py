# app/routers/submitdata.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.submit_service import SubmitService
from app.schemas.pereval import PerevalOut, PerevalCreate
from app.schemas.responses import SubmitResponse, SubmitPatchResponse

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
    return service.get_perevals_by_user_email(user__email)


@router.post("", response_model=SubmitResponse, status_code=status.HTTP_201_CREATED)
def post_submit(payload: PerevalCreate, service: SubmitService = Depends(get_service)):
    """
    POST /submitData
    Возвращает строго {status, message, id}
    """
    try:
        pereval = service.create_pereval(payload)
        return SubmitResponse(status="ok", message="created", id=pereval.id)
    except Exception as e:
        return SubmitResponse(status="error", message=f"creation failed: {e}", id=None)


@router.patch("/{pereval_id}", response_model=SubmitPatchResponse)
def patch_submit(pereval_id: int, payload: dict, service: SubmitService = Depends(get_service)):
    """
    PATCH /submitData/{id}
    Ожидается payload вида {"status": "<new_status>"}
    Возвращает строго {state, message}
    Обновление разрешено только если текущий status == "new"
    """
    new_status = payload.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="status is required in payload")

    obj = service.repo.get_by_id(pereval_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Pereval not found")

    if obj.status != "new":
        raise HTTPException(status_code=409, detail="Only records with status 'new' can be updated")

    updated = service.update_status(pereval_id, new_status)
    return SubmitPatchResponse(state=updated.status, message="status updated")
