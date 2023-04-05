from fastapi import FastAPI
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from starlette.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core import config
from app.core.cache import base_cache


def get_application() -> FastAPI:

    application: FastAPI = FastAPI(
        title=config.PROJECT_NAME,
        description=f"API сервиса {config.PROJECT_NAME}",
        root_path=config.API_ROOT_PATH,
        version=config.VERSION,
        debug=config.DEBUG,
    )

    async def validation_exception_handler(request: Request, exc: ValidationError):
        errors = [
            {"loc": ".".join(error["loc"]), "msg": error["msg"], "type": error["type"]}
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={"detail": errors},
        )

    application.add_exception_handler(
        RequestValidationError, validation_exception_handler
    )

    async def integrity_error_handler(request: Request, exc: IntegrityError):
        # if isinstance(exc.orig, IntegrityError):
        error_detail = str(exc.orig)
        return JSONResponse(
            status_code=400,
            content={
                "detail": error_detail,
                "status_code": 400,
            },
        )

    application.add_exception_handler(IntegrityError, integrity_error_handler)
    # application.add_middleware(BaseHTTPMiddleware, dispatch=log_service_response)

    # application.add_exception_handler(HTTPException, http_error_handler)
    # application.add_exception_handler(RequestValidationError, http422_error_handler)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(
        router,
        prefix=config.API_ROUTE,
    )

    return application


app = get_application()


@app.on_event("startup")
async def startup_event():
    await base_cache.start_up()


@app.on_event("shutdown")
async def shutdown_event():
    await base_cache.gracefully_closing()
