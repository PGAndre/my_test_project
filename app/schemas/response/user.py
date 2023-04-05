from typing import Optional

from pydantic import BaseModel


class UserResponseSchema(BaseModel):
    id: str
    name: str
    surname: str
    patronymic: Optional[str]
    phone_number: str
    email: Optional[str]
    country: str
    country_code: Optional[int]
