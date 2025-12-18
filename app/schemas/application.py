# app/schemas/application.py
"""
応募関連のスキーマ
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ApplicationCreate(BaseModel):
    """応募作成リクエスト"""
    jobId: str
    message: Optional[str] = None
    resumeSubmitted: bool = False
    portfolioSubmitted: bool = False
    coverLetter: Optional[str] = None


class ApplicationUpdate(BaseModel):
    """応募更新リクエスト"""
    status: Optional[str] = None
    notes: Optional[str] = None


class ApplicationItem(BaseModel):
    """応募項目"""
    id: str
    jobId: str
    jobTitle: str
    company: str
    location: str
    salary: str
    matchScore: Optional[int] = None
    status: str
    statusColor: str
    appliedDate: str
    lastUpdate: str
    nextStep: Optional[str] = None
    interviewDate: Optional[str] = None
    documents: dict

    class Config:
        from_attributes = True


class ApplicationDetail(BaseModel):
    """応募詳細"""
    id: str
    jobId: str
    jobTitle: str
    company: str
    location: str
    salary: str
    matchScore: Optional[int] = None
    status: str
    statusColor: str
    statusDetail: Optional[str] = None
    appliedDate: str
    lastUpdate: str
    nextStep: Optional[str] = None
    interviewDate: Optional[str] = None
    message: Optional[str] = None
    notes: Optional[str] = None
    documents: dict

    class Config:
        from_attributes = True


class ApplicationListResponse(BaseModel):
    """応募一覧レスポンス"""
    applications: list[ApplicationItem]
    total: int
