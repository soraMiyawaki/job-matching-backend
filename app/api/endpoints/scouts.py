# app/api/endpoints/scouts.py
"""
スカウトAPI
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import json

from app.schemas.scout import (
    ScoutCreate,
    ScoutUpdate,
    ScoutItem,
    ScoutDetail,
    ScoutListResponse,
)
from app.models.scout import Scout, ScoutStatus
from app.models.user import User, UserRole
from app.db.session import get_db

router = APIRouter()

# TODO: 認証ミドルウェアを追加してユーザーIDを取得
MOCK_USER_ID = "mock-user-id"
MOCK_USER_ROLE = "seeker"  # or "employer"


def scout_to_item(scout: Scout, user_role: str, employer: User = None, seeker: User = None) -> ScoutItem:
    """ScoutモデルをScoutItemに変換"""
    # タグをJSON解析
    tags = []
    if scout.tags:
        try:
            tags = json.loads(scout.tags)
        except:
            pass

    return ScoutItem(
        id=scout.id,
        title=scout.title,
        company=employer.company_name if employer and user_role == "seeker" else None,
        candidateName=seeker.name if seeker and user_role == "employer" else None,
        message=scout.message,
        matchScore=scout.match_score,
        status=scout.status.value,
        createdAt=scout.created_at.strftime("%Y-%m-%d"),
        tags=tags,
    )


def scout_to_detail(scout: Scout, user_role: str, employer: User = None, seeker: User = None) -> ScoutDetail:
    """ScoutモデルをScoutDetailに変換"""
    # タグをJSON解析
    tags = []
    if scout.tags:
        try:
            tags = json.loads(scout.tags)
        except:
            pass

    return ScoutDetail(
        id=scout.id,
        title=scout.title,
        company=employer.company_name if employer and user_role == "seeker" else None,
        candidateName=seeker.name if seeker and user_role == "employer" else None,
        message=scout.message,
        matchScore=scout.match_score,
        status=scout.status.value,
        createdAt=scout.created_at.strftime("%Y-%m-%d"),
        readAt=scout.read_at.isoformat() if scout.read_at else None,
        repliedAt=scout.replied_at.isoformat() if scout.replied_at else None,
        tags=tags,
        jobId=scout.job_id,
    )


@router.get("/", response_model=ScoutListResponse)
async def get_scouts(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    # TODO: current_user: User = Depends(get_current_user)
):
    """
    スカウト一覧を取得（求職者：受信、企業：送信）

    Args:
        status_filter: ステータスフィルター
        db: データベースセッション

    Returns:
        スカウト一覧
    """
    # TODO: 実際のユーザーIDとロールを使用
    user_id = MOCK_USER_ID
    user_role = MOCK_USER_ROLE

    # ユーザーロールに応じてクエリを変更
    if user_role == "seeker":
        # 求職者：受信したスカウト
        query = db.query(Scout).filter(Scout.seeker_id == user_id)
    else:
        # 企業：送信したスカウト
        query = db.query(Scout).filter(Scout.employer_id == user_id)

    # ステータスフィルター
    if status_filter and status_filter != "all":
        try:
            query = query.filter(Scout.status == ScoutStatus(status_filter))
        except ValueError:
            pass

    # スカウトを取得
    scouts = query.order_by(Scout.created_at.desc()).all()

    # ユーザー情報を結合
    items = []
    for scout in scouts:
        employer = db.query(User).filter(User.id == scout.employer_id).first()
        seeker = db.query(User).filter(User.id == scout.seeker_id).first()
        items.append(scout_to_item(scout, user_role, employer, seeker))

    return ScoutListResponse(
        scouts=items,
        total=len(items),
    )


@router.post("/", response_model=ScoutDetail, status_code=status.HTTP_201_CREATED)
async def create_scout(
    request: ScoutCreate,
    db: Session = Depends(get_db),
    # TODO: current_user: User = Depends(get_current_user)
):
    """
    スカウトを送信（企業のみ）

    Args:
        request: スカウト作成リクエスト
        db: データベースセッション

    Returns:
        作成したスカウト
    """
    # TODO: 実際のユーザーIDとロールを使用
    user_id = MOCK_USER_ID
    user_role = MOCK_USER_ROLE

    # 企業のみがスカウトを送信可能
    if user_role != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="企業アカウントのみがスカウトを送信できます"
        )

    # 求職者が存在するか確認
    seeker = db.query(User).filter(
        User.id == request.seekerId,
        User.role == UserRole.SEEKER
    ).first()

    if not seeker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="求職者が見つかりません"
        )

    # スカウトを作成
    scout = Scout(
        id=str(uuid.uuid4()),
        employer_id=user_id,
        seeker_id=request.seekerId,
        job_id=request.jobId,
        title=request.title,
        message=request.message,
        tags=json.dumps(request.tags) if request.tags else None,
        status=ScoutStatus.NEW,
    )

    db.add(scout)
    db.commit()
    db.refresh(scout)

    employer = db.query(User).filter(User.id == user_id).first()
    return scout_to_detail(scout, user_role, employer, seeker)


@router.get("/{scout_id}", response_model=ScoutDetail)
async def get_scout(
    scout_id: str,
    db: Session = Depends(get_db),
    # TODO: current_user: User = Depends(get_current_user)
):
    """
    スカウト詳細を取得

    Args:
        scout_id: スカウトID
        db: データベースセッション

    Returns:
        スカウト詳細
    """
    # TODO: 実際のユーザーIDとロールを使用
    user_id = MOCK_USER_ID
    user_role = MOCK_USER_ROLE

    scout = db.query(Scout).filter(Scout.id == scout_id).first()

    if not scout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="スカウトが見つかりません"
        )

    # アクセス権限チェック
    if user_role == "seeker" and scout.seeker_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このスカウトにアクセスする権限がありません"
        )
    elif user_role == "employer" and scout.employer_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このスカウトにアクセスする権限がありません"
        )

    employer = db.query(User).filter(User.id == scout.employer_id).first()
    seeker = db.query(User).filter(User.id == scout.seeker_id).first()

    return scout_to_detail(scout, user_role, employer, seeker)


@router.put("/{scout_id}", response_model=ScoutDetail)
async def update_scout(
    scout_id: str,
    request: ScoutUpdate,
    db: Session = Depends(get_db),
    # TODO: current_user: User = Depends(get_current_user)
):
    """
    スカウトステータスを更新

    Args:
        scout_id: スカウトID
        request: 更新内容
        db: データベースセッション

    Returns:
        更新後のスカウト
    """
    # TODO: 実際のユーザーIDとロールを使用
    user_id = MOCK_USER_ID
    user_role = MOCK_USER_ROLE

    scout = db.query(Scout).filter(Scout.id == scout_id).first()

    if not scout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="スカウトが見つかりません"
        )

    # アクセス権限チェック（求職者のみが更新可能）
    if user_role != "seeker" or scout.seeker_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このスカウトを更新する権限がありません"
        )

    # ステータスを更新
    try:
        scout.status = ScoutStatus(request.status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無効なステータスです"
        )

    db.commit()
    db.refresh(scout)

    employer = db.query(User).filter(User.id == scout.employer_id).first()
    seeker = db.query(User).filter(User.id == scout.seeker_id).first()

    return scout_to_detail(scout, user_role, employer, seeker)
