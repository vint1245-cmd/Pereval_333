# app/routers/submitdata.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.schemas.pereval import PerevalCreate, PerevalUpdate
from app.schemas.responses import SubmitResponse, SubmitPatchResponse
from app.services.submit_service import SubmitService

router = APIRouter(prefix="/submitData", tags=["submitData"])


@router.post("", response_model=SubmitResponse)
async def submit_data(payload: PerevalCreate, session: AsyncSession = Depends(get_session)):
    service = SubmitService(session)
    result = await service.create_pereval(payload)
    return JSONResponse(status_code=200, content=result)


@router.get("/{pereval_id}")
async def get_pereval(pereval_id: int, session: AsyncSession = Depends(get_session)):
    service = SubmitService(session)
    result = await service.get_pereval(pereval_id)
    return result


@router.get("")
async def list_perevals(user__email: str, session: AsyncSession = Depends(get_session)):
    service = SubmitService(session)
    result = await service.list_by_user_email(user__email)
    return result


@router.patch("/{pereval_id}", response_model=SubmitPatchResponse)
async def update_pereval(pereval_id: int, payload: PerevalUpdate, session: AsyncSession = Depends(get_session)):
    service = SubmitService(session)
    result = await service.update_pereval(pereval_id, payload)
    return JSONResponse(status_code=200, content=result)
