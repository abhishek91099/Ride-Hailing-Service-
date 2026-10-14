import json
import logging
import time
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1 import coupons_router, drivers_router, rides_router, users_router
from app.core.config import settings
from app.core.exceptions import DomainError


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "event"):
            payload["event"] = record.event
        if hasattr(record, "method"):
            payload["method"] = record.method
        if hasattr(record, "path"):
            payload["path"] = record.path
        if hasattr(record, "query"):
            payload["query"] = record.query
        if hasattr(record, "status_code"):
            payload["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            payload["duration_ms"] = record.duration_ms
        if hasattr(record, "request_id"):
            payload["request_id"] = record.request_id
        if hasattr(record, "error"):
            payload["error"] = record.error
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


logger = logging.getLogger("ride_hailing")
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or uuid4().hex
    request.state.request_id = request_id
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.exception(
            "api request failed",
            extra={
                "event": "api_request",
                "method": request.method,
                "path": request.url.path,
                "query": request.url.query,
                "status_code": 500,
                "duration_ms": duration_ms,
                "request_id": request_id,
            },
        )
        raise

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    logger.info(
        "api request completed",
        extra={
            "event": "api_request",
            "method": request.method,
            "path": request.url.path,
            "query": request.url.query,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "request_id": request_id,
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    request_id = getattr(request.state, "request_id", uuid4().hex)
    logger.warning(
        "domain error",
        extra={
            "event": "domain_error",
            "method": request.method,
            "path": request.url.path,
            "request_id": request_id,
            "error": str(exc),
        },
    )
    return JSONResponse(status_code=400, content={"detail": str(exc), "request_id": request_id})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", uuid4().hex)
    logger.exception(
        "unhandled exception",
        extra={
            "event": "unhandled_exception",
            "method": request.method,
            "path": request.url.path,
            "request_id": request_id,
        },
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error", "request_id": request_id})


app.include_router(users_router, prefix=settings.api_v1_prefix)
app.include_router(drivers_router, prefix=settings.api_v1_prefix)
app.include_router(rides_router, prefix=settings.api_v1_prefix)
app.include_router(coupons_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
