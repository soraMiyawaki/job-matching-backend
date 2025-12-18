# app/api/endpoints/employer.py
"""
企業向けAPIエンドポイント
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

router = APIRouter()


# === リクエスト/レスポンスモデル ===

class EmployerRegisterRequest(BaseModel):
    """企業登録リクエスト"""
    name: str
    email: str
    password: str
    companyName: str
    industry: Optional[str] = None


class EmployerResponse(BaseModel):
    """企業情報レスポンス"""
    id: str
    name: str
    email: str
    description: Optional[str] = None
    industry: Optional[str] = None
    companySize: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    logoUrl: Optional[str] = None
    createdAt: str
    updatedAt: str


class EmployerRegisterResponse(BaseModel):
    """企業登録レスポンス"""
    employer: EmployerResponse
    token: str


class JobCreateRequest(BaseModel):
    """求人作成リクエスト"""
    title: str
    description: str
    location: str
    employmentType: str = Field(..., pattern="^(full-time|part-time|contract|internship)$")
    salaryMin: Optional[int] = None
    salaryMax: Optional[int] = None
    requiredSkills: Optional[List[str]] = None
    preferredSkills: Optional[List[str]] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    status: str = Field(default="draft", pattern="^(draft|published|closed)$")


class JobResponse(BaseModel):
    """求人レスポンス"""
    id: str
    employerId: str
    title: str
    description: str
    location: str
    employmentType: str
    salaryMin: Optional[int] = None
    salaryMax: Optional[int] = None
    requiredSkills: Optional[List[str]] = None
    preferredSkills: Optional[List[str]] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    status: str
    embedding: Optional[List[float]] = None
    metadata: Optional[dict] = None
    createdAt: str
    updatedAt: str
    applicationsCount: int = 0


class ChatRequest(BaseModel):
    """AI対話型ヒアリングリクエスト"""
    jobId: str
    message: str
    sessionId: Optional[str] = None


class ChatMessage(BaseModel):
    """チャットメッセージ"""
    id: str
    role: str
    content: str
    timestamp: str


class ChatResponse(BaseModel):
    """AI対話型ヒアリングレスポンス"""
    sessionId: str
    message: ChatMessage
    embedding: Optional[List[float]] = None
    isComplete: bool = False


class DashboardStats(BaseModel):
    """ダッシュボード統計"""
    totalJobs: int
    publishedJobs: int
    draftJobs: int
    closedJobs: int
    totalApplications: int
    pendingApplications: int
    interviewApplications: int
    offerApplications: int


# === エンドポイント ===

@router.post("/register", response_model=EmployerRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_employer(request: EmployerRegisterRequest):
    """企業登録"""
    # TODO: 実際のDB処理を実装
    employer_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    employer = EmployerResponse(
        id=employer_id,
        name=request.name,
        email=request.email,
        industry=request.industry,
        createdAt=now,
        updatedAt=now
    )

    # TODO: JWT生成を実装
    token = f"mock-token-{employer_id}"

    return EmployerRegisterResponse(employer=employer, token=token)


@router.get("/me", response_model=EmployerResponse)
async def get_current_employer():
    """現在の企業情報を取得"""
    # TODO: 認証トークンから企業情報を取得
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required"
    )


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(request: JobCreateRequest):
    """求人を作成"""
    job_id = str(uuid.uuid4())
    employer_id = "mock-employer-id"  # TODO: 認証から取得
    now = datetime.utcnow().isoformat()

    job = JobResponse(
        id=job_id,
        employerId=employer_id,
        title=request.title,
        description=request.description,
        location=request.location,
        employmentType=request.employmentType,
        salaryMin=request.salaryMin,
        salaryMax=request.salaryMax,
        requiredSkills=request.requiredSkills or [],
        preferredSkills=request.preferredSkills or [],
        requirements=request.requirements,
        benefits=request.benefits,
        status=request.status,
        createdAt=now,
        updatedAt=now,
        applicationsCount=0
    )

    return job


@router.get("/jobs", response_model=dict)
async def get_employer_jobs(
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 10
):
    """自社の求人一覧を取得"""
    # TODO: DBから取得
    return {
        "items": [],
        "total": 0,
        "page": page,
        "totalPages": 0
    }


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """求人詳細を取得"""
    # TODO: DB から取得
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Job not found"
    )


@router.post("/jobs/chat", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """AI対話型ヒアリング - メッセージを送信"""
    session_id = request.sessionId or str(uuid.uuid4())

    # TODO: OpenAI APIを使用して応答を生成
    response_message = ChatMessage(
        id=str(uuid.uuid4()),
        role="assistant",
        content="ありがとうございます。さらに詳しく教えていただけますか？",
        timestamp=datetime.utcnow().isoformat()
    )

    return ChatResponse(
        sessionId=session_id,
        message=response_message,
        isComplete=False
    )


@router.get("/jobs/{job_id}/chat", response_model=ChatResponse)
async def get_chat_session(job_id: str):
    """AI対話型ヒアリング - セッションを取得"""
    # TODO: セッションデータを取得
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Chat session not found"
    )


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """ダッシュボードの統計情報を取得"""
    # TODO: 実際の統計を取得
    return DashboardStats(
        totalJobs=5,
        publishedJobs=3,
        draftJobs=2,
        closedJobs=0,
        totalApplications=12,
        pendingApplications=5,
        interviewApplications=4,
        offerApplications=3
    )
