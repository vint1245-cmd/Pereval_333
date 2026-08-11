import re
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, Field

PHONE_PATTERN = re.compile(r"^\+?\d{7,15}$")

class UserBase(BaseModel):
    email: EmailStr = Field(..., example="ivanov@example.com", description="Электронная почта пользователя")
    phone: Optional[str] = Field(None, example="+79991234567", description="Телефон в международном формате, только цифры и +")
    fam: str = Field(..., example="Иванов", description="Фамилия пользователя")
    name: str = Field(..., example="Иван", description="Имя пользователя")
    otc: Optional[str] = Field(None, example="Иванович", description="Отчество пользователя (опционально)")

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
