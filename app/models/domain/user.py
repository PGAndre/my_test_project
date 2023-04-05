from typing import Optional

from app.models.domain.base import DomainModel


class UserDomain(DomainModel):
    id: str
    name: str
    surname: str
    patronymic: Optional[str]
    phone_number: str
    email: Optional[str]
    country: str
    country_code: Optional[int]
