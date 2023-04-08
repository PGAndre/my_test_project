from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

from sqlalchemy import delete
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.db.setup import Base
from app.db.setup import maybe_session
from app.models.domain.base import AnyDomainModel


ModelType = TypeVar("ModelType", bound=Base)


class Repository:

    def __init__(self, model: Type[ModelType], domain_model: Type[AnyDomainModel]):
        self.model = model
        self.domain_model = domain_model

    def make_search_query(self, **kwargs: Dict) -> Select:
        q = select(self.model)
        for key, value in kwargs.items():
            if isinstance(value, list):
                q = q.where(getattr(self.model, key).in_(value))
            else:
                q = q.where(getattr(self.model, key) == value)
        return q

    @maybe_session
    async def create(self, session: AsyncSession, **kwargs: Dict) -> AnyDomainModel:
        instance = self.model(**kwargs)
        session.add(instance)
        await session.flush()
        return self.domain_model(**instance.__dict__)

    @maybe_session
    async def read(self, pk: str, value: Any, session: AsyncSession) -> AnyDomainModel:
        """Может поднять sqlalchemy.exc.NoResultFound"""

        query = select(self.model).where(getattr(self.model, pk) == value)
        instance = await exactly_one(session, query)
        return self.domain_model(**instance.__dict__)

    @maybe_session
    async def update(self, pk: str, session: AsyncSession, **kwargs: Any) -> None:
        q = (
            update(self.model)
            .where(getattr(self.model, pk) == kwargs[pk])
            .values(**kwargs)
        )
        result = await session.execute(q)
        assert (
            result.rowcount == 1
        ), f"Rowcount is {result.rowcount} instead of 1. All changes are rolled back!"

    @maybe_session
    async def delete(self, pk: str, value: Any, session: AsyncSession) -> None:
        """Может поднять sqlalchemy.exc.NoResultFound"""

        query = delete(self.model).where(getattr(self.model, pk) == value)
        await session.execute(query)
        await session.commit()

    @maybe_session
    async def read_many(self, session: AsyncSession, **kwargs) -> List[ModelType]:
        q = self.make_search_query(**kwargs)
        records = await get_list(session, q)
        return [self.domain_model(**x.__dict__) for x in records]

    @maybe_session
    async def upsert(
        self,
        data: Dict,
        pk: str,
        session: AsyncSession,
        constraint: Optional[str] = None,
    ) -> AnyDomainModel:

        if not constraint:
            constraint = f"uq_{self.model.__table__.name}_{pk}"

        statement = (
            insert(self.model)
            .values(**data)
            .on_conflict_do_update(constraint=constraint, set_=data)
        )
        await session.execute(statement)

        item = await self.read(pk=pk, value=data[pk], session=session)
        return item

    @maybe_session
    async def multiple_update(
        self,
        data: List[Dict],
        session: AsyncSession,
    ):
        statement = update(self.model)
        await session.execute(statement, data)

    @maybe_session
    async def read_one(self, session: AsyncSession, **kwargs) -> AnyDomainModel:
        result = await exactly_one(session, self.make_search_query(**kwargs))
        return self.domain_model(**result.__dict__)


async def one_or_none(api_db: AsyncSession, query: Select) -> Optional[ModelType]:
    return (await api_db.execute(query)).unique().scalars().one_or_none()


async def get_list(api_db: AsyncSession, query: Select) -> List[ModelType]:
    return (await api_db.execute(query)).scalars().all()


async def exactly_one(session: AsyncSession, query) -> ModelType:
    """Может поднять sqlalchemy.exc.NoResultFound"""

    return (await session.execute(query)).unique().scalars().one()


async def get_total_rows(api_db: AsyncSession, query: Select) -> int:
    return (
        (await api_db.execute(select(func.count()).select_from(query.subquery())))
        .scalars()
        .one()
    )


async def get_first(api_db: AsyncSession, query: Select) -> Optional[ModelType]:
    return (await api_db.execute(query)).scalars().first()
