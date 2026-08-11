from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.user import UserCreate, UserOut
from app.schemas.coords import CoordsCreate, CoordsOut
from app.schemas.level import LevelCreate, LevelOut
from app.schemas.image import ImageCreate, ImageOut


class PerevalStatus(str, Enum):
    new = "new"
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class PerevalBase(BaseModel):
    beauty_title: Optional[str] = Field(None, example="Перевал Безымянный", description="Красивое название перевала")
    title: Optional[str] = Field(None, example="Безымянный перевал", description="Официальное название")
    other_titles: Optional[str] = Field(None, example="Перевал Икс;Перевал Y", description="Альтернативные названия (через ;)")
    connect: Optional[str] = Field(None, example="г. A - г. B", description="Маршрут, к которому относится перевал")
    add_time: Optional[datetime] = Field(None, example="2024-01-01 12:00:00", description="Дата/время добавления записи")


class PerevalCreate(PerevalBase):
    user: UserCreate
    coords: CoordsCreate
    level: LevelCreate
    images: List[ImageCreate]


class PerevalUpdate(PerevalBase):
    user: Optional[UserCreate] = None
    coords: Optional[CoordsCreate] = None
    level: Optional[LevelCreate] = None
    images: Optional[List[ImageCreate]] = None
    images_to_delete: Optional[List[int]] = Field(None, example=[1, 2], description="ID изображений для удаления")

    model_config = {"from_attributes": True}


class PerevalOut(PerevalBase):
    id: int
    status: PerevalStatus
    user: UserOut
    coords: CoordsOut
    level: LevelOut
    images: List[ImageOut]

    model_config = {"from_attributes": True}
