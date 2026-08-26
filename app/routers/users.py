from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.schemas.response import APIResponse
from app.schemas.user import UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=APIResponse[UserResponse])
def read_user_me(current_user: User = Depends(get_current_active_user)):
    return APIResponse(message="Current user profile retrieved", data=current_user)


@router.get("", response_model=APIResponse[List[UserResponse]])
def read_users(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    users = UserService.get_users(
        db, skip=skip, limit=limit, search=search, is_active=is_active
    )
    return APIResponse(message="Users retrieved successfully", data=users)
