from fastapi import APIRouter
from fastapi import status

from app.core.cache import base_cache
from app.core.cache import get_handler


router = APIRouter()


@router.get(
    "/users/redis/keys",
    summary="Получение кэшированных ключей",
    status_code=status.HTTP_200_OK,
)
async def get_cache_request() -> list[str]:
    keys = await base_cache.get_all_keys()
    decoded_keys = [elem.decode("utf8") for elem in keys]
    return decoded_keys


@router.delete(
    "/users/redis/keys",
    summary="Удаление кэшированных данных",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def get_cache_request():
    await base_cache.delete_all_keys()


@router.get(
    "/healthcheck",
    name="service:healthcheck",
)
async def get_healthcheck():
    handler = get_handler(key="test", ttl_seconds=30)
    components = [
        dict(
            component="redis",
            liveness=await handler.is_alive(),
        )
    ]

    return components
