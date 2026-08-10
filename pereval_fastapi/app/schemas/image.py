from pydantic import BaseModel


class ImageBase(BaseModel):
    data: str  # base64
    title: str | None = None


class ImageCreate(ImageBase):
    pass


class ImageOut(ImageBase):
    id: int

    class Config:
        from_attributes = True
