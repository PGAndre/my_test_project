from functools import lru_cache

from pydantic import BaseSettings


class APPSettings(BaseSettings):
    PROJECT_NAME: str = "My_Test_Project"
    VERSION: str = "1.0.0"

    DEBUG: bool = False
    # ENV: str = "TEST"

    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:passw0rd@localhost:55432/my_project"
    )
    DB_POOL_SIZE: int = 10

    API_ROUTE: str = ""
    API_ROOT_PATH: str = ""

    DADATA_APP_URL: str = "https://suggestions.dadata.ru/suggestions"
    DADATA_APP_KEY: str = "Token b835755f51ad8ad13358c80e27fb5c3e14221caa"
    CACHING: bool = True
    REDIS_URL: str = "redis://localhost"

    # class Config:
    #     env_file = ".env"


config = APPSettings()


@lru_cache()
def get_app_settings() -> APPSettings:
    return APPSettings()
