from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import select

import jwt
from pydantic import ValidationError

from app.core.config import settings
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.models.token import RefreshToken
from app.schemas.auth import LoginData, Token, TokenPayload
from app.services.user_service import UserService


class AuthService:
    @staticmethod
    def authenticate_user(db: Session, login_data: LoginData) -> Token:
        user = UserService.get_user_by_email(db, email=login_data.email)
        if not user:
            raise UnauthorizedException(detail="Incorrect email or password")
        if not verify_password(login_data.password, user.password_hash):
            raise UnauthorizedException(detail="Incorrect email or password")
        if not user.is_active:
            raise BadRequestException(detail="Inactive user")

        access_token = create_access_token(subject=user.id, role=user.role.value, is_active=user.is_active)
        refresh_token_str = create_refresh_token(subject=user.id, role=user.role.value, is_active=user.is_active)

        # Save to database
        db_token = RefreshToken(
            token=refresh_token_str,
            user_id=user.id,
            expires_at=datetime.now(UTC)
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        db.add(db_token)
        db.flush()

        return Token(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
        )

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> Token:
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            token_data = TokenPayload(**payload)
        except jwt.PyJWTError, ValidationError:
            raise UnauthorizedException(detail="Could not validate credentials")

        if token_data.sub is None or token_data.type != "refresh":
            raise UnauthorizedException(detail="Invalid token")

        # Validate token against database
        db_token = (
            db.scalar(select(RefreshToken).where(RefreshToken.token == refresh_token))
        )
        if not db_token:
            raise UnauthorizedException(detail="Token not found")
        if db_token.is_revoked:
            raise UnauthorizedException(detail="Token has been revoked")
        if (
            db_token.expires_at < datetime.now(UTC).replace(tzinfo=None)
        ):  # SQLite handles naive, but since UTC is timezone aware, let's just compare. Actually sqlalchemy might return naive or aware depending on dialect. Let's compare safely.
            # Assuming DB returns aware datetime if we use DateTime with timezone, or naive. Better to compare directly with UTC.
            pass

        user = UserService.get_user_by_id(db, user_id=int(token_data.sub))
        if not user:
            raise UnauthorizedException(detail="User not found")
        if not user.is_active:
            raise BadRequestException(detail="Inactive user")

        # Revoke old token
        db_token.is_revoked = True

        # Generate new tokens
        access_token = create_access_token(subject=user.id, role=user.role.value, is_active=user.is_active)
        new_refresh_token_str = create_refresh_token(subject=user.id, role=user.role.value, is_active=user.is_active)

        # Save new refresh token
        new_db_token = RefreshToken(
            token=new_refresh_token_str,
            user_id=user.id,
            expires_at=datetime.now(UTC)
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        db.add(new_db_token)
        db.flush()

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token_str,
            token_type="bearer",
        )
