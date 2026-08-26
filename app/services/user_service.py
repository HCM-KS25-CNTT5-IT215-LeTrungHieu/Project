from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.security import get_password_hash
from app.models.user import RoleEnum, User
from app.schemas.user import UserRegister


class UserService:
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        return db.scalar(select(User).where(User.email == email))

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User | None:
        return db.scalar(select(User).where(User.id == user_id))

    @staticmethod
    def create_user(db: Session, user_in: UserRegister) -> User:
        existing_user = UserService.get_user_by_email(db, user_in.email)
        if existing_user:
            raise BadRequestException(detail="Email already registered")

        hashed_password = get_password_hash(user_in.password)

        db_user = User(
            email=user_in.email,
            password_hash=hashed_password,
            full_name=user_in.full_name,
            role=RoleEnum.USER.value,
            is_active=True,
        )
        db.add(db_user)
        db.flush()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> list[User]:
        stmt = select(User)
        if search:
            stmt = stmt.where(
                or_(
                    User.full_name.ilike(f"%{search}%"), User.email.ilike(f"%{search}%")
                )
            )
        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)

        return list(db.scalars(stmt.offset(skip).limit(limit)).all())
