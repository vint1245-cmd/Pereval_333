from typing import Optional
from pydantic import BaseModel, field_validator
import base64

class ImageBase(BaseModel):
    title: Optional[str] = None
    data: str  # base64 string

class ImageCreate(ImageBase):
    @field_validator("data")
    def validate_base64(cls, v: str) -> str:
        try:
            if v.startswith("data:"):
                v = v.split(",", 1)[1]
            base64.b64decode(v, validate=True)
        except Exception:
            raise ValueError("data must be valid base64")
        return v

class ImageOut(ImageBase):
    id: int

    model_config = {"from_attributes": True}
