from fastapi import HTTPException

from app.clients.base import BaseAPI
from app.clients.exceptions import BadRequestAPIException
from app.clients.exceptions import ClientErrorAPIException
from app.clients.external_api.dadata.schemas.response.dadata import (
    DadataCountryResponse,
)
from app.core.cache import get_handler
from app.core.settings import config


class DadataGatewayAPI(BaseAPI):

    base_url = f"{config.DADATA_APP_URL}"
    CACHE_NAMESPACE = "my_project"

    async def get_country_info(self, country: str):

        cache_handler = get_handler(
            key=f"my_project_get_country_info_{country}",
            ttl_seconds=60 * 60 * 5,
        )
        try:
            status_code, response = await self.cached_request(
                cache_handler=cache_handler,
                headers={
                    "Content-Type": "application/json",
                    "authorization": config.DADATA_APP_KEY,
                },
                method="post",
                path="/api/4_1/rs/suggest/country",
                json_data={
                    "query": str(country),
                },
            )
        except (ClientErrorAPIException, BadRequestAPIException) as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)

        return DadataCountryResponse(**response)


dadata_api = DadataGatewayAPI()
