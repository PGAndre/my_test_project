from unittest.mock import AsyncMock

from httpx import AsyncClient
import pytest

from app.clients.external_api.dadata.schemas.response.dadata import DadataCountryData
from app.clients.external_api.dadata.schemas.response.dadata import (
    DadataCountryResponse,
)
from app.clients.external_api.dadata.schemas.response.dadata import (
    DadataCountrySuggestion,
)
from app.main import app


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def new_user_data():
    return {
        "name": "Иван",
        "surname": "Иванов",
        "patronymic": "Иванович",
        "phone_number": "79161234567",
        "email": "ivan@example.com",
        "country": "Россия",
    }


@pytest.fixture
def dadata_country_response():
    data = DadataCountryData(
        code="123",
        alfa2="RU",
        alfa3="RUS",
        name_short="Россия",
        name="Российская Федерация",
    )
    suggestion = DadataCountrySuggestion(
        value="Россия", unrestricted_value="Россия", data=data
    )
    response = DadataCountryResponse(suggestions=[suggestion])
    return response


async def test_create_user(
    new_user_data, dadata_country_response, mocker, async_client
):
    mocker.patch(
        "app.clients.external_api.dadata.clients.dadata.dadata_api.get_country_info",
        new=AsyncMock(return_value=dadata_country_response),
    )

    response = await async_client.post("v1/users", json=new_user_data)

    assert response.status_code == 201
    # Удаляем пользователя
    phone_number = new_user_data["phone_number"]
    response = await async_client.delete(f"v1/users/{phone_number}")
    assert response.status_code == 204
    # Проверяем, что пользователь действительно удален
    response = await async_client.get(f"v1/users/{phone_number}")
    assert response.status_code == 404
