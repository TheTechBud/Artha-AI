from fastapi import Request
from fastapi.responses import JSONResponse
from observability.logger import get_logger

logger = get_logger("middleware.errors")


async def global_error_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "code": "INTERNAL_ERROR",
            "detail": str(exc),
        },
    )
