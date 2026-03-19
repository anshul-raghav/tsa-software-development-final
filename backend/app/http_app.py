"""
FastAPI app factory and global exception handlers.

Composes CORS, request logging, validation/domain/generic exception handlers,
and mounts all API v1 route modules under a configurable prefix.
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import TouchMapError, touchmap_exception_to_http
from app.api.routes import (
    debug_routes,
    explore_routes,
    guidance_routes,
    health_routes,
    locate_routes,
    scan_routes,
    task_routes,
)


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

    # Middleware: log every request and response
    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        logger.info(f">> {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"<< {request.method} {request.url} => {response.status_code}")
        return response

    # Exception handlers: validation, domain, and unhandled
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        errors = [
            {k: str(v) if not isinstance(v, (str, int, float, bool, list, dict, type(None))) else v
             for k, v in field_error.items()}
            for field_error in exc.errors()
        ]
        logger.error(f"Validation error on {request.method} {request.url}: {errors}")
        return JSONResponse(
            status_code=422,
            content={"message": "Validation error", "detail": errors},
        )

    @app.exception_handler(TouchMapError)
    async def handle_touchmap_error(request: Request, exc: TouchMapError):
        http_exc = touchmap_exception_to_http(exc)
        return JSONResponse(
            status_code=http_exc.status_code,
            content=http_exc.detail,
        )

    @app.exception_handler(Exception)
    async def handle_unhandled_error(request: Request, exc: Exception):
        logger.error(f"Unhandled error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "detail": str(exc)},
        )

    # Route registration: all v1 endpoints under prefix
    prefix = settings.api_v1_prefix
    app.include_router(health_routes.router, prefix=prefix)
    app.include_router(scan_routes.router, prefix=prefix)
    app.include_router(task_routes.router, prefix=prefix)
    app.include_router(locate_routes.router, prefix=prefix)
    app.include_router(explore_routes.router, prefix=prefix)
    app.include_router(guidance_routes.router, prefix=prefix)
    app.include_router(debug_routes.router, prefix=prefix)

    logger.info(f"{settings.app_name} initialized")
    return app


app = create_app()
