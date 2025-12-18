# app/models/job.py
"""
求人モデル
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class JobStatus(str, enum.Enum):
    """求人ステータス"""
    DRAFT = "draft"  # 下書き
    PUBLISHED = "published"  # 公開中
    CLOSED = "closed"  # 募集終了


class EmploymentType(str, enum.Enum):
    """雇用形態"""
    FULL_TIME = "full-time"  # 正社員
    PART_TIME = "part-time"  # パート・アルバイト
    CONTRACT = "contract"  # 契約社員
    INTERNSHIP = "internship"  # インターン


class Job(Base):
    """求人テーブル"""
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True)
    employer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # 基本情報
    title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(200), nullable=False)
    employment_type = Column(Enum(EmploymentType), nullable=False)

    # 給与情報
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_text = Column(String(200), nullable=True)

    # 必須・歓迎スキル
    required_skills = Column(Text, nullable=True)  # JSON文字列
    preferred_skills = Column(Text, nullable=True)  # JSON文字列

    # 詳細情報
    requirements = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON文字列

    # リモートワーク
    remote = Column(Boolean, default=False, nullable=False)

    # ステータス
    status = Column(Enum(JobStatus), default=JobStatus.DRAFT, nullable=False)
    featured = Column(Boolean, default=False, nullable=False)

    # エンベディング（AIマッチング用）
    embedding = Column(Text, nullable=True)  # JSON文字列（ベクトル）

    # メタデータ
    meta_data = Column(Text, nullable=True)  # JSON文字列

    # 日時
    posted_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Job {self.title} by {self.company}>"
