import time
from fastapi import Request
from observability.logger import get_logger

logger = get_logger("middleware.logging")


async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(
        f"{request.method} {request.url.path} → {response.status_code} "
        f"({duration*1000:.1f}ms)"
    )
    return response
