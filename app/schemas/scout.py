# app/schemas/scout.py
"""
スカウト関連のスキーマ
"""
from pydantic import BaseModel
from typing import Optional


class ScoutCreate(BaseModel):
    """スカウト作成リクエスト"""
    seekerId: str
    jobId: Optional[str] = None
    title: str
    message: str
    tags: Optional[list[str]] = None


class ScoutUpdate(BaseModel):
    """スカウト更新リクエスト"""
    status: str


class ScoutItem(BaseModel):
    """スカウト項目"""
    id: str
    title: str
    company: Optional[str] = None
    candidateName: Optional[str] = None
    message: str
    matchScore: Optional[int] = None
    status: str
    createdAt: str
    tags: list[str] = []

    class Config:
        from_attributes = True


class ScoutDetail(BaseModel):
    """スカウト詳細"""
    id: str
    title: str
    company: Optional[str] = None
    candidateName: Optional[str] = None
    message: str
    matchScore: Optional[int] = None
    status: str
    createdAt: str
    readAt: Optional[str] = None
    repliedAt: Optional[str] = None
    tags: list[str] = []
    jobId: Optional[str] = None

    class Config:
        from_attributes = True


class ScoutListResponse(BaseModel):
    """スカウト一覧レスポンス"""
    scouts: list[ScoutItem]
    total: int
