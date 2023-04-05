from fastapi import APIRouter

from app.api.routes.v1.tech import router as tech_router
from app.api.routes.v1.user import router as user_router


router = APIRouter()

router.include_router(user_router, tags=["Пользователи"], prefix="/v1")
router.include_router(tech_router, tags=["Служебные"], prefix="/v1/tech")
