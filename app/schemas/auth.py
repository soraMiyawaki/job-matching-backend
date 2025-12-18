# app/schemas/auth.py
"""
認証関連のスキーマ
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    """登録リクエスト"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., pattern="^(seeker|employer)$")

    # 企業の場合
    companyName: Optional[str] = None
    industry: Optional[str] = None


class LoginRequest(BaseModel):
    """ログインリクエスト"""
    email: EmailStr
    password: str


class LineLinkRequest(BaseModel):
    """LINE連携リクエスト"""
    lineUserId: str


class TokenResponse(BaseModel):
    """トークンレスポンス"""
    accessToken: str
    tokenType: str = "bearer"
    expiresIn: int


class UserResponse(BaseModel):
    """ユーザーレスポンス"""
    id: str
    email: str
    name: str
    role: str
    lineLinked: bool = False
    profileCompletion: str = "0"
    createdAt: datetime

    # 求職者用フィールド
    skills: Optional[list[str]] = None
    experienceYears: Optional[str] = None
    desiredSalaryMin: Optional[str] = None
    desiredSalaryMax: Optional[str] = None
    desiredLocation: Optional[str] = None
    desiredEmploymentType: Optional[str] = None

    # 企業用フィールド
    companyName: Optional[str] = None
    industry: Optional[str] = None
    companySize: Optional[str] = None
    companyDescription: Optional[str] = None

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """認証レスポンス"""
    user: UserResponse
    token: TokenResponse
