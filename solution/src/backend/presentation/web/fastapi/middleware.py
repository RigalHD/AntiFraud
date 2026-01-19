from datetime import UTC, datetime
from uuid import uuid4

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from backend.presentation.web.fastapi.exc_handler import ErrorResponse
from backend.presentation.web.serializer import serializer


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = request.headers.get("content-type", "")

            if "application/json" not in content_type:
                response = ErrorResponse(
                    code="UNSUPPORTED_CONTENT_TYPE",
                    message="Неподдерживаемый Content-Type",
                    trace_id=uuid4(),
                    timestamp=datetime.now(tz=UTC),
                    path=request.url.path,
                )
                return JSONResponse(content=serializer.dump(response), status_code=400)

        return await call_next(request)
