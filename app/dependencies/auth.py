import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
)
from app.db.database import get_db
from app.models.user import RoleEnum
from app.schemas.auth import TokenPayload
from app.schemas.user import CurrentUser

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.PyJWTError, ValidationError):
        raise UnauthorizedException(detail="Could not validate credentials")

    if token_data.sub is None or token_data.role is None or token_data.is_active is None:
        raise UnauthorizedException(detail="Could not validate credentials")

    return CurrentUser(
        id=int(token_data.sub),
        role=token_data.role,
        is_active=token_data.is_active
    )


def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if not current_user.is_active:
        raise ForbiddenException(detail="Inactive user")
    return current_user


def get_current_admin_user(
    current_user: CurrentUser = Depends(get_current_active_user),
) -> CurrentUser:
    if current_user.role != RoleEnum.ADMIN.value:
        raise ForbiddenException(detail="The user doesn't have enough privileges")
    return current_user
