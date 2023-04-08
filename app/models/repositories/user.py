from typing import Any
from typing import Dict

from fastapi import HTTPException
from fastapi import status
from sqlalchemy import delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.external_api.dadata.clients.dadata import dadata_api
from app.clients.external_api.dadata.schemas.response.dadata import (
    DadataCountryResponse,
)
from app.db.base import get_list
from app.db.base import Repository
from app.db.setup import in_transaction
from app.db.setup import maybe_session
from app.db.tables.users import User as UserTable
from app.models.domain.user import UserDomain


class UserRepo:
    #используем композицию для доступа к репозиторию DB
    model = UserTable
    domain_model = UserDomain
    db_repo = Repository(model=model, domain_model=domain_model)

    @classmethod
    async def check_exists(cls, **fields: Dict[str, str]):
        query = cls.db_repo.make_search_query(**fields)

        async with in_transaction() as db:
            users = await get_list(api_db=db, query=query)

        if len(users) > 0:
            field_details = ", ".join([f"{key}" for key, value in fields.items()])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Пользователь с таким {field_details} уже существует",
            )

    @classmethod
    async def get_user(cls, pk: str, value: Any):
        try:
            user: UserDomain = await cls.db_repo.read(pk=pk, value=value)
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с таким {pk} не найден",
            )
        if user.country:
            try:
                country_data: DadataCountryResponse = await dadata_api.get_country_info(
                    user.country
                )
                if country_data:
                    user.country_code = country_data.suggestions[0].data.code
            except Exception:
                pass

        return user

    @classmethod
    @maybe_session
    async def delete(cls, pk: str, value: Any, session: AsyncSession) -> None:
        query = delete(cls.model).where(getattr(cls.model, pk) == value)
        user_to_delete = await session.execute(query)
        if user_to_delete.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с таким {pk} не найден",
            )
