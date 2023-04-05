from pydantic import ValidationError
import pytest

from app.schemas.request.user import CreateUserRequestSchema


@pytest.fixture
def valid_user_data():
    return {
        "name": "Иван",
        "surname": "Иванов",
        "patronymic": "Иванович",
        "phone_number": "71234567890",
        "email": "test@example.com",
        "country": "Россия",
    }


@pytest.fixture
def invalid_user_data():
    return {
        "name": "A" * 51,
        "surname": "B" * 51,
        "patronymic": "C" * 51,
        "phone_number": "7123456789",
        "email": "not_an_email",
        "country": "D" * 51,
    }


def test_create_user_request_schema_valid_data(valid_user_data):
    user = CreateUserRequestSchema(**valid_user_data)
    assert user


@pytest.mark.parametrize("field_name", ["name", "surname", "patronymic", "country"])
def test_create_user_request_schema_max_length(field_name):
    invalid_data = {
        "name": "A" * 51,
        "surname": "B" * 51,
        "patronymic": "C" * 51,
        "country": "D" * 51,
        "phone_number": "71234567890",
    }
    invalid_data[field_name] = "X" * 51
    with pytest.raises(ValidationError):
        CreateUserRequestSchema(**invalid_data)


@pytest.mark.parametrize(
    "phone_number", ["81234567890", "71234567834234323", "not_a_number"]
)
def test_create_user_request_schema_validate_phone_number(phone_number):
    invalid_data = {
        "name": "Иван",
        "surname": "Иванов",
        "patronymic": "Иванович",
        "phone_number": phone_number,
        "email": "test@example.com",
        "country": "Россия",
    }
    with pytest.raises(ValidationError):
        CreateUserRequestSchema(**invalid_data)


@pytest.mark.parametrize("field_name", ["name", "surname", "patronymic"])
def test_create_user_request_schema_validate_cyrillic_characters(field_name):
    invalid_data = {
        "name": "Иван",
        "surname": "Иванов",
        "patronymic": "Иванович",
        "phone_number": "71234567890",
        "email": "test@example.com",
        "country": "Россия",
    }
    invalid_data[field_name] = "Not Cyrillic"
    with pytest.raises(ValidationError):
        CreateUserRequestSchema(**invalid_data)


def test_create_user_request_schema_optional_email():
    user_data = {
        "name": "Иван",
        "surname": "Иванов",
        "patronymic": "Иванович",
        "phone_number": "71234567890",
        "country": "Россия",
    }
    user = CreateUserRequestSchema(**user_data)
    assert user.email is None
