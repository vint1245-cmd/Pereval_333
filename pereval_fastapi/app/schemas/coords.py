from pydantic import BaseModel

class CoordsBase(BaseModel):
    latitude: float
    longitude: float
    height: int

class CoordsCreate(CoordsBase):
    pass

class CoordsOut(CoordsBase):
    id: int

    model_config = {"from_attributes": True}
