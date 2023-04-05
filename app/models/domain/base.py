from typing import TypeVar

from pydantic import BaseModel


class DomainModel(BaseModel):
    def __str__(self):
        return repr(self)

    class Config:
        allow_mutation = True
        orm_mode = True


AnyDomainModel = TypeVar("AnyDomainModel", bound=DomainModel)  # TODO
