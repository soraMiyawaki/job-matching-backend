# app/models/user.py
"""
ユーザーモデル（求職者・企業）
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Enum
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class UserRole(str, enum.Enum):
    """ユーザーロール"""
    SEEKER = "seeker"  # 求職者
    EMPLOYER = "employer"  # 企業


class User(Base):
    """ユーザーテーブル"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    # LINE連携
    line_user_id = Column(String(100), unique=True, nullable=True, index=True)
    line_linked_at = Column(DateTime(timezone=True), nullable=True)

    # 求職者固有フィールド
    skills = Column(Text, nullable=True)  # JSON文字列
    experience_years = Column(String(20), nullable=True)
    desired_salary_min = Column(String(50), nullable=True)
    desired_salary_max = Column(String(50), nullable=True)
    desired_location = Column(String(100), nullable=True)
    desired_employment_type = Column(String(50), nullable=True)
    resume_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)

    # 企業固有フィールド
    company_name = Column(String(200), nullable=True)
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    company_description = Column(Text, nullable=True)
    company_website = Column(String(500), nullable=True)
    company_location = Column(String(200), nullable=True)
    company_logo_url = Column(String(500), nullable=True)

    # プロフィール完成度
    profile_completion = Column(String(10), default="0", nullable=True)

    # 共通フィールド
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
