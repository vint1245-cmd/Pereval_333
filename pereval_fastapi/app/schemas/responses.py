# app/schemas/responses.py
from typing import Optional

from pydantic import BaseModel


class SubmitResponse(BaseModel):
    status: int
    message: Optional[str] = None
    id: Optional[int] = None

    model_config = {"from_attributes": True}


class SubmitPatchResponse(BaseModel):
    state: int
    message: str

    model_config = {"from_attributes": True}
