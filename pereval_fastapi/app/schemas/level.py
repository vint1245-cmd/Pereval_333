from typing import Optional
from pydantic import BaseModel, Field

class LevelBase(BaseModel):
    winter: Optional[str] = Field(None, example="1A", description="Категория сложности зимой")
    summer: Optional[str] = Field(None, example="1A", description="Категория сложности летом")
    autumn: Optional[str] = Field(None, example="1A", description="Категория сложности осенью")
    spring: Optional[str] = Field(None, example="1A", description="Категория сложности весной")

class LevelCreate(LevelBase):
    pass

class LevelOut(LevelBase):
    id: int

    model_config = {"from_attributes": True}
