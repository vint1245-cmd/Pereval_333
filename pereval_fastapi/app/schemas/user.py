# app/schemas/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    fam: str
    name: str
    otc: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True
