# app/schemas/pereval.py
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.schemas.user import UserCreate, UserOut
from app.schemas.coords import CoordsCreate, CoordsOut
from app.schemas.level import LevelCreate, LevelOut
from app.schemas.image import ImageCreate, ImageOut


class PerevalBase(BaseModel):
    beauty_title: Optional[str] = None
    title: Optional[str] = None
    other_titles: Optional[str] = None
    connect: Optional[str] = None


class PerevalCreate(PerevalBase):
    user: UserCreate
    coords: CoordsCreate
    level: LevelCreate
    images: List[ImageCreate]


class PerevalOut(PerevalBase):
    id: int
    status: str
    add_time: datetime
    user: UserOut
    coords: CoordsOut
    level: LevelOut
    images: List[ImageOut]

    class Config:
        orm_mode = True
