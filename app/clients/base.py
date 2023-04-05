from typing import Any
from typing import Literal
from typing import Optional
from typing import Tuple

from aiohttp import BasicAuth
from aiohttp import ContentTypeError
from aiohttp.client import ClientSession

from app.clients.exceptions import BadRequestAPIException
from app.clients.exceptions import ClientErrorAPIException
from app.clients.exceptions import ServerErrorAPIException
from app.core.cache import RedisCacheBaseHandler


__all__ = [
    "BaseAPI",
]


class BaseAPI:
    base_url: Optional[str] = None

    async def cached_request(
        self,
        cache_handler: RedisCacheBaseHandler,
        method: Literal["get", "post", "put", "patch", "delete"],
        path: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
    ):

        status_code = 200
        response = await cache_handler.get_value()

        if response is None:
            status_code, response = await self._request(
                method=method,
                path=path,
                headers=headers,
                params=params,
                json_data=json_data,
            )
            if status_code == 200:
                await cache_handler.set_value(response)
        return status_code, response

    @classmethod
    async def _request(
        cls,
        method: Literal["get", "post", "put", "patch", "delete"],
        path: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        json_data: Optional[Any] = None,
        auth: Optional[BasicAuth] = None,
    ) -> Tuple[int, Any]:
        _url = f"{cls.base_url}{path}"
        _headers = {
            "Content-Type": "application/json",
        }

        if headers:
            _headers.update(headers)

        _params = params or {}
        _json = json_data or {}

        async with ClientSession() as session:
            _session_method = getattr(session, method)
            async with _session_method(
                url=_url,
                headers=_headers,
                params=_params,
                json=_json,
                auth=auth,
            ) as response:
                try:
                    response_json = await response.json()
                except ContentTypeError:
                    response_json = {}

        if response.status == 400:
            detail = response_json.get("detail")
            raise BadRequestAPIException(
                response.status,
                detail if detail else response_json.get("errors"),
            )
        elif 400 < response.status <= 499:
            detail = response_json.get("detail")
            raise ClientErrorAPIException(
                response.status,
                detail if detail else response_json.get("errors"),
            )
        elif response.status >= 500:
            raise ServerErrorAPIException(response.status, response._body)
        else:

            return response.status, response_json

    @classmethod
    async def get_alive(cls) -> tuple[int, Any]:
        status_code, response = 0, {}

        try:
            status_code, response = await cls._request(
                method="get",
                path="/live",
            )
        except (
            ClientErrorAPIException,
            BadRequestAPIException,
            ServerErrorAPIException,
        ) as e:
            status_code = e.status_code

        return status_code, response
