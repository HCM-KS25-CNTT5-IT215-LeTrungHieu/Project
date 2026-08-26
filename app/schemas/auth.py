from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: str | None = None
    role: str | None = None
    is_active: bool | None = None
    type: str | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LoginData(BaseModel):
    email: EmailStr
    password: str
