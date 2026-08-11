from typing import Optional
from pydantic import BaseModel

class LevelBase(BaseModel):
    winter: Optional[str] = None
    summer: Optional[str] = None
    autumn: Optional[str] = None
    spring: Optional[str] = None

class LevelCreate(LevelBase):
    pass

class LevelOut(LevelBase):
    id: int

    model_config = {"from_attributes": True}
