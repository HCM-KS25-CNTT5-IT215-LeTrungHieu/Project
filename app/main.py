from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import (
    CustomException,
    custom_exception_handler,
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.routers import api_router
from app.schemas.response import APIResponse

app = FastAPI(title="Project API")
app.include_router(api_router)

# Add Exception Handlers
app.add_exception_handler(CustomException, custom_exception_handler)  # type: ignore
app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
app.add_exception_handler(Exception, global_exception_handler)


@app.get("/health", response_model=APIResponse[dict])
def health_check():
    return APIResponse(message="System is healthy", data={"status": "ok"})
