from typing import Optional
import re

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import validator


class CreateUserRequestSchema(BaseModel):
    name: str
    surname: str
    patronymic: str
    phone_number: str
    email: Optional[EmailStr] = None
    country: str

    @validator("name", "surname", "country")
    def max_length(cls, value):
        if len(value) > 50:
            raise ValueError("Максимальная длинна поля - 50 символов")
        return value

    @validator("phone_number")
    def validate_phone_number(cls, value):
        if not (value.isdigit() and value.startswith("7") and len(value) <= 11):
            raise ValueError('Невалидный номер. (Номер должен начинаться с "7")')
        return value

    @validator("email", pre=True, always=False)
    def validate_e(cls, val):
        if val == "":
            return None
        return val

    @validator("name", "surname", "patronymic")
    def validate_cyrillic_characters(cls, value: str) -> str:
        if not re.fullmatch(r"[\u0400-\u04FF\s\-]+", value):
            raise ValueError(
                "Only Cyrillic characters, spaces, and hyphens are allowed"
            )
        return value
