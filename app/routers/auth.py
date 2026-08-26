from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import LoginData, RefreshTokenRequest, Token
from app.schemas.response import APIResponse
from app.schemas.user import UserRegister, UserResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    user = UserService.create_user(db, user_in=user_in)
    return APIResponse(message="User created successfully", data=user)


@router.post("/login", response_model=APIResponse[Token])
def login(login_data: LoginData, db: Session = Depends(get_db)):
    token = AuthService.authenticate_user(db, login_data=login_data)
    return APIResponse(message="Login successful", data=token)


@router.post("/refresh", response_model=APIResponse[Token])
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    token = AuthService.refresh_access_token(db, refresh_token=request.refresh_token)
    return APIResponse(message="Token refreshed successfully", data=token)
