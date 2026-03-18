from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import TouchMapError, touchmap_exception_to_http
from app.api.routes import health, scan, task, locate, explore, guidance, debug


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="TouchMap: Audio-guided navigation for flat physical interfaces",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(f">> {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"<< {request.method} {request.url} => {response.status_code}")
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        errors = [
            {k: str(v) if not isinstance(v, (str, int, float, bool, list, dict, type(None))) else v
             for k, v in err.items()}
            for err in exc.errors()
        ]
        logger.error(f"Validation error on {request.method} {request.url}: {errors}")
        return JSONResponse(
            status_code=422,
            content={"message": "Validation error", "detail": errors},
        )

    @app.exception_handler(TouchMapError)
    async def touchmap_error_handler(request: Request, exc: TouchMapError):
        http_exc = touchmap_exception_to_http(exc)
        return JSONResponse(
            status_code=http_exc.status_code,
            content=http_exc.detail,
        )

    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "detail": str(exc)},
        )

    prefix = settings.api_v1_prefix
    app.include_router(health.router, prefix=prefix)
    app.include_router(scan.router, prefix=prefix)
    app.include_router(task.router, prefix=prefix)
    app.include_router(locate.router, prefix=prefix)
    app.include_router(explore.router, prefix=prefix)
    app.include_router(guidance.router, prefix=prefix)
    app.include_router(debug.router, prefix=prefix)

    logger.info(f"{settings.app_name} initialized")
    return app


app = create_app()
