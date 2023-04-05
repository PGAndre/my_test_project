from typing import Any
from typing import Optional

from aioredis.client import Redis as RedisClient
from orjson import orjson
import aioredis

from app.core.settings import config


class RedisBaseCache:
    def __init__(
        self,
        aioredis_client: Optional[RedisClient] = None,
    ):
        self._client: Optional[RedisClient] = aioredis_client

    async def start_up(self):
        if config.CACHING:
            self._client = await aioredis.from_url(
                url=config.REDIS_URL,
            )
        else:
            return None

    async def set_value(self, key: str, value: bytes, ttl_seconds: int = 30):
        if self._client:
            await self._client.set(
                name=key,
                value=value,
                ex=ttl_seconds,
            )

    async def get_value(self, key: str) -> Optional[str]:
        if self._client:
            cached_value = await self._client.get(name=key)
            return cached_value

    async def delete_all_keys(self):
        if self._client:
            async for key in self._client.scan_iter("*"):
                await self._client.delete(key)

    async def get_all_keys(self):
        if self._client:
            keys = await self._client.keys("*")
            return keys

    async def gracefully_closing(self):
        if self._client:
            await self._client.close()
            self._client = None

    async def is_alive(self) -> bool:
        is_alive = False
        test_value = 100

        try:
            await self.set_value(key="test_key", value=orjson.dumps(test_value))
            cached_value = await self.get_value(key="test_key")
            is_alive = cached_value == test_value
        except Exception:
            pass
        return is_alive


class RedisCacheBaseHandler:
    def __init__(
        self,
        base_cache: RedisBaseCache,
        key: str,
        ttl_seconds: Optional[int] = None,
    ):
        self.cache: RedisBaseCache = base_cache
        self.key: str = key
        self.ttl_seconds: Optional[int] = ttl_seconds

    async def set_value(
        self,
        value: Any,
        ttl_seconds: Optional[int] = None,
    ):
        if self.ttl_seconds is None and ttl_seconds is None:
            raise ValueError("ttl_seconds does not exist")

        await self.cache.set_value(
            key=self.key,
            value=orjson.dumps(value),
            ttl_seconds=ttl_seconds or self.ttl_seconds,
        )

    async def get_value(self) -> Optional[Any]:
        cache_data = await self.cache.get_value(
            key=self.key,
        )
        ret_value = orjson.loads(cache_data) if cache_data else None

        return ret_value

    async def is_alive(self) -> bool:
        is_alive = False
        test_value = 100

        try:
            await self.set_value(test_value)
            cached_value = await self.get_value()
            is_alive = cached_value == test_value
        except Exception:
            pass
        return is_alive

    async def delete_all_keys(self):
        await self.cache.delete_all_keys()

    async def get_all_keys(self):
        return self.cache.get_all_keys()


base_cache = RedisBaseCache()


def get_handler(
    key: str,
    ttl_seconds: Optional[int] = None,
) -> RedisCacheBaseHandler:
    return RedisCacheBaseHandler(base_cache, key, ttl_seconds)
