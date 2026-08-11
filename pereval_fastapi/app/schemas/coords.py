from pydantic import BaseModel, Field

class CoordsBase(BaseModel):
    latitude: float = Field(..., example=45.123456, description="Широта в десятичном формате")
    longitude: float = Field(..., example=39.123456, description="Долгота в десятичном формате")
    height: int = Field(..., example=1500, description="Высота над уровнем моря в метрах")

class CoordsCreate(CoordsBase):
    pass

class CoordsOut(CoordsBase):
    id: int

    model_config = {"from_attributes": True}
