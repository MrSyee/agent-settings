# Pattern 7: Structured Logging (Environment-Aware + Trace ID)
# - JSON formatter for production, colored console for local
# - Per-request trace ID propagation via ContextVar
# - Request/response logging middleware with slow-request warnings
#
# Directory structure:
#   app/core/
#   ├── context.py                  # Request-scoped ContextVars
#   ├── logging/
#   │   ├── logger.py               # Logger setup (env-aware formatter selection)
#   │   ├── logger_formatter.py     # JSON formatter for production
#   │   └── logger_util.py          # Shutdown helper
#   └── middleware/
#       └── logging.py              # Request/response logging middleware

# -------------------------------------------------------------------
# Step 1: Request-scoped context variable (core/context.py)
# -------------------------------------------------------------------
from contextvars import ContextVar

trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="-")


# -------------------------------------------------------------------
# Step 2: JSON formatter for production (core/logging/logger_formatter.py)
# -------------------------------------------------------------------
import json
import logging
from datetime import UTC, datetime
from typing import ClassVar


class JsonFormatter(logging.Formatter):
    """Structured JSON formatter for production logging."""

    LEVEL_MAP: ClassVar[dict[str, str]] = {
        "DEBUG": "DEBUG",
        "INFO": "INFO",
        "WARNING": "WARN",
        "ERROR": "ERROR",
        "CRITICAL": "FATAL",
    }

    EXCLUDE_FIELDS: ClassVar[frozenset[str]] = frozenset({
        "name", "msg", "args", "levelname", "levelno", "pathname",
        "filename", "module", "exc_info", "exc_text", "stack_info",
        "lineno", "funcName", "created", "msecs", "relativeCreated",
        "thread", "threadName", "processName", "process", "taskName",
    })

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as a single-line JSON string."""
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": self.LEVEL_MAP.get(record.levelname, record.levelname),
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_record["error_message"] = self.formatException(record.exc_info)
            if record.exc_info[0]:
                log_record["error_code"] = record.exc_info[0].__name__

        # Collect extra fields passed via logger.info("msg", extra={...})
        for key, value in record.__dict__.items():
            if key not in self.EXCLUDE_FIELDS:
                if isinstance(value, (str | int | float | bool | type(None))):
                    log_record[key] = value

        return json.dumps(log_record, ensure_ascii=False)


# -------------------------------------------------------------------
# Step 3: Logger setup — env-aware (core/logging/logger.py)
# -------------------------------------------------------------------
import sys

from app.core.config import settings
from app.core.context import trace_id_ctx
from app.core.logging.logger_formatter import JsonFormatter


class TraceIdFilter(logging.Filter):
    """Inject trace_id from ContextVar into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = trace_id_ctx.get()
        return True


class ColoredConsoleFormatter(logging.Formatter):
    """Local development formatter with ANSI colors + trace_id."""

    LEVEL_COLORS: dict[str, str] = {
        "DEBUG": "\033[36m", "INFO": "\033[32m", "WARNING": "\033[33m",
        "ERROR": "\033[31m", "CRITICAL": "\033[35;1m",
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        from datetime import datetime
        dt = datetime.fromtimestamp(record.created)
        ts = dt.strftime("%Y-%m-%d %H:%M:%S") + f".{int(record.msecs):03d}"
        color = self.LEVEL_COLORS.get(record.levelname, "")
        trace_id = getattr(record, "trace_id", "-")
        return (
            f"\033[36m{ts}{self.RESET} "
            f"{color}{record.levelname:<5}{self.RESET} "
            f"\033[33m[{trace_id}]{self.RESET} "
            f"\033[35m{record.filename}:{record.lineno}{self.RESET} "
            f": {color}{record.getMessage()}"
        )


def _setup_logger() -> logging.Logger:
    """Build the application logger.

    - local env  -> colored console output
    - other envs -> structured JSON to stdout
    """
    log = logging.getLogger("my-service")
    log.setLevel(getattr(logging, settings.log_level, logging.INFO))
    log.propagate = False

    log.addFilter(TraceIdFilter())

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.log_level, logging.INFO))

    if settings.env == "local":
        handler.setFormatter(ColoredConsoleFormatter())
    else:
        handler.setFormatter(JsonFormatter())

    log.addHandler(handler)
    return log


# Module-level singleton
logger = _setup_logger()


# -------------------------------------------------------------------
# Step 4: Request/response logging middleware (core/middleware/logging.py)
# -------------------------------------------------------------------
import time
import uuid
from typing import Final

from fastapi import Request

from app.core.context import trace_id_ctx
from app.core.logging.logger import logger

SLOW_REQUEST_THRESHOLD_MS: Final[int] = 3000
VERY_SLOW_REQUEST_THRESHOLD_MS: Final[int] = 5000


async def set_logging(request: Request, call_next):
    """Log every request with duration, method, status, and trace_id."""
    # Propagate or generate trace_id
    trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())
    trace_id_ctx.set(trace_id)

    # Skip noisy health-check paths
    if request.url.path.endswith("/healthcheck"):
        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        return response

    start_time = time.time()

    # Capture request body for mutating methods
    request_body = None
    if request.method in ("POST", "PUT", "PATCH"):
        body_bytes = await request.body()
        if body_bytes:
            request_body = body_bytes.decode("utf-8")

            async def receive():
                return {"type": "http.request", "body": body_bytes}
            request._receive = receive      # re-inject consumed body

    response = await call_next(request)

    duration_ms = round((time.time() - start_time) * 1000)
    log_extra: dict[str, str | int] = {
        "path": request.url.path,
        "method": request.method,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
    }
    if request_body:
        log_extra["content_str"] = request_body

    # Warn on slow requests
    if duration_ms > VERY_SLOW_REQUEST_THRESHOLD_MS:
        logger.warning(f"[Middleware] VERY SLOW request (>{VERY_SLOW_REQUEST_THRESHOLD_MS}ms)", extra=log_extra)
    elif duration_ms > SLOW_REQUEST_THRESHOLD_MS:
        logger.warning(f"[Middleware] Slow request (>{SLOW_REQUEST_THRESHOLD_MS}ms)", extra=log_extra)
    else:
        logger.info("[Middleware] request processed", extra=log_extra)

    response.headers["X-Trace-ID"] = trace_id
    return response


# -------------------------------------------------------------------
# Step 5: Register middleware in app factory (main.py)
# -------------------------------------------------------------------
# from starlette.middleware.base import BaseHTTPMiddleware
# from app.core.middleware.logging import set_logging
#
# def create_app() -> FastAPI:
#     app = FastAPI(title="My Service", lifespan=lifespan)
#     app.add_middleware(BaseHTTPMiddleware, dispatch=set_logging)
#     return app
