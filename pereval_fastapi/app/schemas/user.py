from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    phone: str | None = None
    fam: str
    name: str
    otc: str | None = None


class UserCreate(UserBase):
    pass


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True
