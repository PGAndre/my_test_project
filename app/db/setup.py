from contextlib import asynccontextmanager
from functools import wraps

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core import config


DATABASE_URL = config.DATABASE_URL


engine = create_async_engine(
    DATABASE_URL,
    echo=config.DEBUG,
    pool_size=config.DB_POOL_SIZE,
    future=True,
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=True
)

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)


@asynccontextmanager
async def in_transaction() -> AsyncSession:
    session = async_session()
    await session.begin()
    try:
        yield session
        await session.commit()
    except BaseException:
        await session.rollback()
        raise
    finally:
        await session.close()


def maybe_session(func):
    """
    Передает вызываемой функции сессию без изменений если она подается снаружи, однако
    если ессия не была подана, то запускает функцию с одноразовой сессии так же
    передавая её вызываемой функции.

    Удобно когда пишется группа методов для которых важно иметь возможность
    работать в одной транзакции. Так же удобно когда наличие транзакции не имеет значения.

    !!! Конвеншен при использовании:
    - Декорируемая функция должна иметь в сигнатуре jобязательный параметр session: AsyncSession.
    - При вызове декорируемой функции обязательно передавать сессию именно кейвордом в виде session=X
        либо не передавай её вообще.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        session = kwargs.get("session")

        if session:
            value = await func(*args, **kwargs)
        else:
            async with in_transaction() as new_session:
                value = await func(*args, **kwargs, session=new_session)
        return value

    return wrapper
