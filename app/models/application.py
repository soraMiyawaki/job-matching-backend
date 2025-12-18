# app/models/application.py
"""
応募モデル
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class ApplicationStatus(str, enum.Enum):
    """応募ステータス"""
    SCREENING = "screening"  # 書類選考中
    INTERVIEW = "interview"  # 面接予定・面接中
    OFFERED = "offered"  # 内定
    REJECTED = "rejected"  # 不合格
    WITHDRAWN = "withdrawn"  # 辞退


class Application(Base):
    """応募テーブル"""
    __tablename__ = "applications"

    id = Column(String(36), primary_key=True)
    seeker_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)

    # ステータス
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.SCREENING, nullable=False)
    status_detail = Column(String(100), nullable=True)  # 「一次面接待ち」など
    status_color = Column(String(20), default="yellow", nullable=True)  # UI表示用

    # マッチスコア
    match_score = Column(Integer, nullable=True)

    # 次のステップ
    next_step = Column(String(100), nullable=True)
    interview_date = Column(DateTime(timezone=True), nullable=True)

    # 提出書類
    resume_submitted = Column(String(10), default="false", nullable=True)
    portfolio_submitted = Column(String(10), default="false", nullable=True)
    cover_letter = Column(Text, nullable=True)

    # メッセージ・メモ
    message = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # 日時
    applied_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Application {self.id} - Seeker:{self.seeker_id} Job:{self.job_id}>"
