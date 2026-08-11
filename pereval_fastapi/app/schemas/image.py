from typing import Optional
from pydantic import BaseModel, field_validator, Field
import base64

class ImageBase(BaseModel):
    title: Optional[str] = Field(None, example="Седловина", description="Подпись к изображению")
    data: str = Field(..., example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA...", description="Изображение в base64, можно с префиксом data:...;base64,")

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
