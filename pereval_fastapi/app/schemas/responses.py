# app/schemas/responses.py
from pydantic import BaseModel

class SubmitResponse(BaseModel):
    status: str
    message: str
    id: int | None

    model_config = {"from_attributes": True}


class SubmitPatchResponse(BaseModel):
    state: str
    message: str

    model_config = {"from_attributes": True}
