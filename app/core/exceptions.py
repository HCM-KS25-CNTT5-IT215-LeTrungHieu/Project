from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.response import APIResponse


class CustomException(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class NotFoundException(CustomException):
    def __init__(self, detail: str = "Not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedException(CustomException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class BadRequestException(CustomException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ForbiddenException(CustomException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


from typing import Any, Sequence

def format_pydantic_errors(errors: Sequence[Any]) -> dict[str, str]:
    formatted_errors = {}
    for error in errors:
        loc = ".".join(str(l) for l in error.get("loc", []) if l != "body")
        if not loc:
            loc = "body"
        formatted_errors[loc] = str(error.get("msg", "Unknown error"))
    return formatted_errors


def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(message=exc.detail, error=exc.detail).model_dump(),
    )


def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(message=str(exc.detail), error=exc.detail).model_dump(),
    )


def validation_exception_handler(request: Request, exc: RequestValidationError):
    formatted_errors = format_pydantic_errors(exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=APIResponse(
            message="Validation Error", error=formatted_errors
        ).model_dump(),
    )


def global_exception_handler(request: Request, exc: Exception):

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse(
            message="Internal Server Error", error=str(exc)
        ).model_dump(),
    )
