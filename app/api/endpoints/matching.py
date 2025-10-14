# app/api/endpoints/matching.py
"""
AIマッチング関連のAPIエンドポイント
"""
from fastapi import APIRouter, HTTPException
from typing import List
import logging

from app.schemas.matching import (
    MatchingRequest,
    MatchingResponse,
    JobRecommendationResponse,
    JobAnalysisRequest,
    JobAnalysisResponse,
    CareerChatRequest,
    CareerChatResponse,
    MatchingExplanationRequest,
    MatchingExplanationResponse,
)
from app.core.dependencies import MatchingServiceDep, ConversationServiceDep
from app.core.exceptions import MatchingError, OpenAIError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/recommend", response_model=MatchingResponse)
async def recommend_jobs(
    request: MatchingRequest,
    matching_service: MatchingServiceDep
):
    """
    求職者プロフィールに基づいて求人をレコメンド

    Args:
        request: マッチングリクエスト（求職者プロフィール、求人リスト、top_k）
        matching_service: マッチングサービス（依存性注入）

    Returns:
        マッチング結果（レコメンデーションリスト、統計情報）
    """
    try:

        # 求職者プロフィールと求人リストを辞書形式に変換
        seeker_profile = request.seeker_profile.model_dump()
        available_jobs = [job.model_dump() for job in request.available_jobs]

        logger.info(
            f"Matching request: {len(available_jobs)} jobs, top_k={request.top_k}"
        )

        # レコメンデーション実行
        recommendations = matching_service.recommend_jobs(
            seeker_profile=seeker_profile,
            available_jobs=available_jobs,
            top_k=request.top_k
        )

        # レスポンス形式に変換
        recommendation_responses = [
            JobRecommendationResponse(**rec.to_dict())
            for rec in recommendations
        ]

        response = MatchingResponse(
            recommendations=recommendation_responses,
            total_jobs=len(available_jobs),
            filtered_jobs=len(recommendations)
        )

        logger.info(
            f"Matching completed: {len(recommendations)} recommendations generated"
        )

        return response

    except MatchingError as e:
        logger.error(f"Matching error in recommend_jobs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in recommend_jobs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"マッチング処理中にエラーが発生しました: {str(e)}"
        )


@router.get("/health")
async def health_check(matching_service: MatchingServiceDep):
    """
    マッチングサービスのヘルスチェック

    Args:
        matching_service: マッチングサービス（依存性注入）

    Returns:
        サービスのステータス
    """
    try:
        return {
            "status": "healthy",
            "service": "matching",
            "embedding_dim": matching_service.embedding_service.embedding_dim
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="マッチングサービスが利用できません"
        )


@router.post("/analyze-job", response_model=JobAnalysisResponse)
async def analyze_job(
    request: JobAnalysisRequest,
    conversation_service: ConversationServiceDep
):
    """
    OpenAI APIを使って求人とのマッチング分析を生成

    Args:
        request: 求人分析リクエスト
        conversation_service: 会話サービス（依存性注入）

    Returns:
        AI生成の分析テキスト
    """
    try:
        seeker_profile = request.seeker_profile.model_dump()
        job_data = request.job.model_dump()

        analysis = conversation_service.generate_job_analysis(
            seeker_profile=seeker_profile,
            job_data=job_data,
            match_score=request.match_score
        )

        return JobAnalysisResponse(analysis=analysis)

    except OpenAIError as e:
        logger.error(f"OpenAI error in analyze_job: {str(e)}", exc_info=True)
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error in analyze_job: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"求人分析中にエラーが発生しました: {str(e)}"
        )


@router.post("/career-chat", response_model=CareerChatResponse)
async def career_chat(
    request: CareerChatRequest,
    conversation_service: ConversationServiceDep
):
    """
    キャリアに関する会話

    Args:
        request: キャリア相談リクエスト
        conversation_service: 会話サービス（依存性注入）

    Returns:
        AIの返答
    """
    try:
        seeker_profile = request.seeker_profile.model_dump()
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]

        reply = conversation_service.chat_about_career(
            message=request.message,
            conversation_history=conversation_history,
            seeker_profile=seeker_profile
        )

        return CareerChatResponse(reply=reply)

    except OpenAIError as e:
        logger.error(f"OpenAI error in career_chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error in career_chat: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"会話処理中にエラーが発生しました: {str(e)}"
        )


@router.post("/explain-matching", response_model=MatchingExplanationResponse)
async def explain_matching(
    request: MatchingExplanationRequest,
    conversation_service: ConversationServiceDep
):
    """
    マッチング結果全体の説明を生成

    Args:
        request: マッチング説明リクエスト
        conversation_service: 会話サービス（依存性注入）

    Returns:
        AI生成の説明テキスト
    """
    try:
        seeker_profile = request.seeker_profile.model_dump()
        recommendations = [
            {
                "job_data": rec.job.model_dump(),
                "match_score": rec.match_score
            }
            for rec in request.recommendations
        ]

        explanation = conversation_service.generate_matching_explanation(
            seeker_profile=seeker_profile,
            recommendations=recommendations
        )

        return MatchingExplanationResponse(explanation=explanation)

    except OpenAIError as e:
        logger.error(f"OpenAI error in explain_matching: {str(e)}", exc_info=True)
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error in explain_matching: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"説明生成中にエラーが発生しました: {str(e)}"
        )
