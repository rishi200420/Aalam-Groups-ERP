from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging import logger


def _cors_headers_for(request: Request) -> dict[str, str]:
    """Build CORS headers for responses that bypass CORSMiddleware.

    Starlette routes handlers registered for the base ``Exception`` class into
    ServerErrorMiddleware, which wraps CORSMiddleware from the outside. That
    means CORSMiddleware never sees (and never headers-tags) responses coming
    out of our generic 500 handler below, so the browser treats a perfectly
    valid JSON error body as a CORS failure and surfaces it to the frontend as
    an opaque "Network Error" instead of the actual message. We add the same
    headers CORSMiddleware would have added, by hand, only here.
    """
    origin = request.headers.get("origin")
    if not origin or origin not in settings.cors_origins_list:
        return {}
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
        "Vary": "Origin",
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
                "data": None,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        safe_errors = []
        for error in exc.errors():
            error = dict(error)
            error.pop("ctx", None)
            safe_errors.append(error)
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Validation error",
                "data": {"errors": jsonable_encoder(safe_errors)},
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error",
                "data": None,
            },
            headers=_cors_headers_for(request),
        )
