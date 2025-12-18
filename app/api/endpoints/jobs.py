# app/api/endpoints/jobs.py
"""
求人API（求職者向け）
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.schemas.job import (
    JobListItem,
    JobDetail,
    JobSearchRequest,
    JobListResponse,
)
from app.models.job import Job, JobStatus
from app.db.session import get_db

router = APIRouter()


def job_to_list_item(job: Job) -> JobListItem:
    """JobモデルをJobListItemに変換"""
    # タグをJSON解析
    tags = []
    if job.tags:
        try:
            tags = json.loads(job.tags)
        except:
            pass

    # 給与情報を文字列化
    salary = job.salary_text or ""
    if not salary and job.salary_min and job.salary_max:
        salary = f"{job.salary_min}万円～{job.salary_max}万円"
    elif not salary and job.salary_min:
        salary = f"{job.salary_min}万円～"

    return JobListItem(
        id=job.id,
        title=job.title,
        company=job.company,
        location=job.location,
        salary=salary,
        employmentType=job.employment_type.value,
        remote=job.remote,
        tags=tags,
        description=job.description,
        postedDate=job.posted_date.isoformat() if job.posted_date else None,
        featured=job.featured,
    )


def job_to_detail(job: Job) -> JobDetail:
    """JobモデルをJobDetailに変換"""
    # タグをJSON解析
    tags = []
    if job.tags:
        try:
            tags = json.loads(job.tags)
        except:
            pass

    # 要件をリスト化
    requirements = []
    if job.requirements:
        requirements = [req.strip() for req in job.requirements.split('\n') if req.strip()]

    # 福利厚生をリスト化
    benefits = []
    if job.benefits:
        benefits = [ben.strip() for ben in job.benefits.split('\n') if ben.strip()]

    # 給与情報を文字列化
    salary = job.salary_text or ""
    if not salary and job.salary_min and job.salary_max:
        salary = f"{job.salary_min}万円～{job.salary_max}万円"
    elif not salary and job.salary_min:
        salary = f"{job.salary_min}万円～"

    return JobDetail(
        id=job.id,
        title=job.title,
        company=job.company,
        location=job.location,
        salary=salary,
        employmentType=job.employment_type.value,
        remote=job.remote,
        tags=tags,
        description=job.description,
        requirements=requirements,
        benefits=benefits,
        postedDate=job.posted_date.isoformat() if job.posted_date else None,
        featured=job.featured,
    )


@router.get("/", response_model=JobListResponse)
async def get_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    求人一覧を取得

    Args:
        page: ページ番号
        per_page: 1ページあたりの件数
        db: データベースセッション

    Returns:
        求人一覧
    """
    # 公開中の求人のみを取得
    query = db.query(Job).filter(Job.status == JobStatus.PUBLISHED)

    # 総件数を取得
    total = query.count()

    # ページネーション
    offset = (page - 1) * per_page
    jobs = query.order_by(Job.posted_date.desc()).offset(offset).limit(per_page).all()

    # レスポンスを作成
    job_items = [job_to_list_item(job) for job in jobs]

    return JobListResponse(
        jobs=job_items,
        total=total,
        page=page,
        perPage=per_page,
    )


@router.get("/{job_id}", response_model=JobDetail)
async def get_job(job_id: str, db: Session = Depends(get_db)):
    """
    求人詳細を取得

    Args:
        job_id: 求人ID
        db: データベースセッション

    Returns:
        求人詳細
    """
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.status == JobStatus.PUBLISHED
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="求人が見つかりません"
        )

    return job_to_detail(job)


@router.post("/search", response_model=JobListResponse)
async def search_jobs(
    request: JobSearchRequest,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    求人を検索

    Args:
        request: 検索条件
        page: ページ番号
        per_page: 1ページあたりの件数
        db: データベースセッション

    Returns:
        検索結果
    """
    # クエリを構築
    query = db.query(Job).filter(Job.status == JobStatus.PUBLISHED)

    # キーワード検索
    if request.query:
        search_pattern = f"%{request.query}%"
        query = query.filter(
            (Job.title.like(search_pattern)) |
            (Job.company.like(search_pattern)) |
            (Job.description.like(search_pattern))
        )

    # 勤務地フィルター
    if request.location:
        query = query.filter(Job.location.like(f"%{request.location}%"))

    # 雇用形態フィルター
    if request.employmentType:
        query = query.filter(Job.employment_type == request.employmentType)

    # リモートフィルター
    if request.remote is not None:
        query = query.filter(Job.remote == request.remote)

    # 最低年収フィルター
    if request.salaryMin:
        query = query.filter(Job.salary_min >= request.salaryMin)

    # 総件数を取得
    total = query.count()

    # ページネーション
    offset = (page - 1) * per_page
    jobs = query.order_by(Job.posted_date.desc()).offset(offset).limit(per_page).all()

    # レスポンスを作成
    job_items = [job_to_list_item(job) for job in jobs]

    return JobListResponse(
        jobs=job_items,
        total=total,
        page=page,
        perPage=per_page,
    )
