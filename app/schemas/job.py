# app/schemas/job.py
"""
求人関連のスキーマ
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class JobListItem(BaseModel):
    """求人リスト項目"""
    id: str
    title: str
    company: str
    location: str
    salary: str
    employmentType: str
    remote: bool
    matchScore: Optional[int] = None
    tags: list[str] = []
    description: str
    postedDate: Optional[str] = None
    featured: bool = False

    class Config:
        from_attributes = True


class JobDetail(BaseModel):
    """求人詳細"""
    id: str
    title: str
    company: str
    location: str
    salary: str
    employmentType: str
    remote: bool
    matchScore: Optional[int] = None
    tags: list[str] = []
    description: str
    requirements: list[str] = []
    benefits: list[str] = []
    postedDate: Optional[str] = None
    featured: bool = False

    class Config:
        from_attributes = True


class JobSearchRequest(BaseModel):
    """求人検索リクエスト"""
    query: Optional[str] = None
    location: Optional[str] = None
    employmentType: Optional[str] = None
    remote: Optional[bool] = None
    salaryMin: Optional[int] = None
    tags: Optional[list[str]] = None


class JobListResponse(BaseModel):
    """求人一覧レスポンス"""
    jobs: list[JobListItem]
    total: int
    page: int = 1
    perPage: int = 20
