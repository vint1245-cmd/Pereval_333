from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

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
    beauty_title: Optional[str] = None
    title: Optional[str] = None
    other_titles: Optional[str] = None
    connect: Optional[str] = None
    add_time: Optional[datetime] = None


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
    images_to_delete: Optional[List[int]] = None

    model_config = {"from_attributes": True}


class PerevalOut(PerevalBase):
    id: int
    status: PerevalStatus
    user: UserOut
    coords: CoordsOut
    level: LevelOut
    images: List[ImageOut]

    model_config = {"from_attributes": True}
