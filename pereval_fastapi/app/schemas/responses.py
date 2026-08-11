# app/schemas/responses.py
from typing import Optional

from pydantic import BaseModel, Field


class SubmitResponse(BaseModel):
    status: int = Field(..., example=200, description="Код статуса операции (целое число)")
    message: Optional[str] = Field(None, example=None, description="Текст сообщения при ошибке или null при успехе")
    id: Optional[int] = Field(None, example=42, description="Идентификатор созданной записи")

    model_config = {"from_attributes": True}


class SubmitPatchResponse(BaseModel):
    state: int = Field(..., example=1, description="1 — успешно, 0 — ошибка")
    message: str = Field(..., example="Запись успешно отредактирована", description="Текст результата операции")

    model_config = {"from_attributes": True}
