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
from app.models.user import RoleEnum, User
from app.schemas.auth import TokenPayload

security = HTTPBearer()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except jwt.PyJWTError, ValidationError:
        raise UnauthorizedException(detail="Could not validate credentials")

    if token_data.sub is None:
        raise UnauthorizedException(detail="Could not validate credentials")

    user = db.scalar(select(User).where(User.id == int(token_data.sub)))
    if not user:
        raise NotFoundException(detail="User not found")
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise ForbiddenException(detail="Inactive user")
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role != RoleEnum.ADMIN.value:
        raise ForbiddenException(detail="The user doesn't have enough privileges")
    return current_user
