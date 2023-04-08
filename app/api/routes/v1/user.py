from fastapi import APIRouter
from fastapi import status

from app.models.repositories.user import UserRepo
from app.logic import user as logic_user
from app.schemas.request.user import CreateUserRequestSchema
from app.schemas.response.user import UserResponseSchema


router = APIRouter()


@router.post(
    "/users",
    summary="создание пользователя",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseSchema,
    responses={
        status.HTTP_201_CREATED: {"description": "Информация о созданном пользователе"},
    },
)
async def create_user_request(
    new_user: CreateUserRequestSchema,
) -> UserResponseSchema:
    user = await logic_user.create_user(user=new_user)
    response = UserResponseSchema(**dict(user))
    return response


@router.get(
    "/users/{phone_number}",
    summary="Получение данных о пользователе",
    status_code=status.HTTP_200_OK,
    response_model=UserResponseSchema,
    responses={
        status.HTTP_200_OK: {"description": "Информация о пользователе"},
        status.HTTP_404_NOT_FOUND: {"description": "Пользователь не найден"},
    },
)
async def get_user_request(
    phone_number: str,
) -> UserResponseSchema:
    user = await UserRepo.get_user(pk="phone_number", value=phone_number)
    response = UserResponseSchema(**dict(user))
    return response


@router.delete(
    "/users/{phone_number}",
    summary="Удаление пользователя",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Пользователь удален"},
        status.HTTP_404_NOT_FOUND: {"description": "Пользователь не найден"},
    },
)
async def delete_user_request(
    phone_number: str,
) -> None:
    await UserRepo.db_repo.delete(pk="phone_number", value=phone_number)
