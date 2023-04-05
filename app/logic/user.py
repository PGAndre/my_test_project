from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.external_api.dadata.clients.dadata import dadata_api
from app.clients.external_api.dadata.schemas.response.dadata import (
    DadataCountryResponse,
)
from app.db.repositories.user import UserRepo
from app.db.setup import maybe_session
from app.models.domain.user import UserDomain
from app.schemas.request.user import CreateUserRequestSchema


@maybe_session
async def create_user(
    user: CreateUserRequestSchema, session: AsyncSession
) -> UserDomain:
    if user.email:
        await UserRepo.check_exists(**dict(email=user.email))
    await UserRepo.check_exists(**dict(phone_number=user.phone_number))
    user = await UserRepo.create(session=session, **dict(user))
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
