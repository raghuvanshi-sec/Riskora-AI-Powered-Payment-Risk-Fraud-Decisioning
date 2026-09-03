from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uuid

def create_error_response(status_code: int, message: str, request_id: str, details: dict = None):
    """
    Standardized error response structure as required by ARM-002 and ARM-005.
    """
    error_content = {
        "error": {
            "code": status_code,
            "message": message,
            "request_id": request_id
        }
    }
    if details:
        error_content["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=error_content)


def add_exception_handlers(app: FastAPI):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        request_id = str(uuid.uuid4()) # In a real app, this would be extracted from request context/middleware
        return create_error_response(
            status_code=exc.status_code,
            message=str(exc.detail),
            request_id=request_id
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = str(uuid.uuid4())
        return create_error_response(
            status_code=422,
            message="Validation Error",
            request_id=request_id,
            details={"errors": exc.errors()}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        request_id = str(uuid.uuid4())
        # Do not expose internal server errors details to the client
        return create_error_response(
            status_code=500,
            message="Internal Server Error",
            request_id=request_id
        )
