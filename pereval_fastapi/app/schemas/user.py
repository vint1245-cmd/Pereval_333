import re
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator

PHONE_PATTERN = re.compile(r"^\+?\d{7,15}$")

class UserBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    fam: str
    name: str
    otc: Optional[str] = None

    @field_validator("phone")
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.replace(" ", "")
        if not PHONE_PATTERN.match(normalized):
            raise ValueError("phone must be in format +79991234567 or 79991234567")
        return normalized

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    id: int

    model_config = {"from_attributes": True}
