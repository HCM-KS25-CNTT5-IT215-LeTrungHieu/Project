from typing import Any

from pydantic import BaseModel


class APIResponse[T](BaseModel):
    message: str = "Success"
    data: T | None = None
    error: Any | None = None
