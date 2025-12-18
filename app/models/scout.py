# app/models/scout.py
"""
スカウトモデル
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class ScoutStatus(str, enum.Enum):
    """スカウトステータス"""
    NEW = "new"  # 新着
    READ = "read"  # 既読
    REPLIED = "replied"  # 返信済み
    DECLINED = "declined"  # 辞退


class Scout(Base):
    """スカウトテーブル"""
    __tablename__ = "scouts"

    id = Column(String(36), primary_key=True)
    employer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    seeker_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=True, index=True)

    # スカウト内容
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)

    # マッチスコア
    match_score = Column(Integer, nullable=True)

    # ステータス
    status = Column(Enum(ScoutStatus), default=ScoutStatus.NEW, nullable=False)

    # タグ
    tags = Column(Text, nullable=True)  # JSON文字列

    # 日時
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    replied_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Scout {self.id} - Employer:{self.employer_id} Seeker:{self.seeker_id}>"
