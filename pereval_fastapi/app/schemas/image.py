# app/schemas/image.py
from typing import Optional
from pydantic import BaseModel, validator
import base64


class ImageBase(BaseModel):
    title: Optional[str] = None
    data: str  # base64 string


class ImageCreate(ImageBase):
    @validator("data")
    def validate_base64(cls, v: str) -> str:
        try:
            # allow data URI prefixes, strip if present
            if v.startswith("data:"):
                v = v.split(",", 1)[1]
            base64.b64decode(v, validate=True)
        except Exception:
            raise ValueError("data must be valid base64")
        return v


class ImageOut(ImageBase):
    id: int

    class Config:
        orm_mode = True
