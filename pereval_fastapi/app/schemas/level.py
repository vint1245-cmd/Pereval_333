from pydantic import BaseModel


class LevelBase(BaseModel):
    winter: str | None = None
    summer: str | None = None
    autumn: str | None = None
    spring: str | None = None


class LevelCreate(LevelBase):
    pass


class LevelOut(LevelBase):
    id: int

    class Config:
        from_attributes = True
