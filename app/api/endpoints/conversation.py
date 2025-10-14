# app/api/endpoints/conversation.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import logging
import uuid
from datetime import datetime
import json
from pathlib import Path

from app.core.dependencies import (
    OpenAIServiceDep,
    ConversationStorageDep,
    VectorSearchServiceDep,
    SettingsDep
)
from app.core.exceptions import OpenAIError, StorageError, NotFoundError

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    recommendations: Optional[List[Dict[str, Any]]] = None


class ConversationHistoryResponse(BaseModel):
    conversations: List[Dict[str, Any]]


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    openai_service: OpenAIServiceDep,
    storage: ConversationStorageDep,
    settings: SettingsDep
):
    """
    会話型AIマッチング - チャットエンドポイント

    ユーザーとの会話を通じて求人条件を抽出し、最適な求人を提案します。
    """
    try:

        # 会話IDの生成または取得
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # 既存の会話履歴を読み込み
        conversation_data = storage.load_conversation(request.user_id, conversation_id)

        if conversation_data:
            messages = conversation_data.get("messages", [])
        else:
            messages = []

        # ユーザーメッセージを追加
        messages.append({
            "role": "user",
            "content": request.message
        })

        # AIの応答を生成
        ai_response = openai_service.generate_chat_response(messages)

        # AIの応答を履歴に追加
        messages.append({
            "role": "assistant",
            "content": ai_response
        })

        # 会話を保存
        storage.save_conversation(
            user_id=request.user_id,
            conversation_id=conversation_id,
            messages=messages,
            metadata={
                "created_at": conversation_data.get("created_at") if conversation_data else datetime.now().isoformat()
            }
        )

        # 一定のメッセージ数に達したら、条件を抽出して求人検索
        recommendations = None
        if len(messages) >= 6:  # 3往復以上の会話
            try:
                recommendations = await _extract_and_search_jobs(
                    openai_service,
                    storage,
                    request.user_id,
                    messages
                )
            except Exception as e:
                logger.warning(f"Failed to extract preferences and search: {e}")

        return ChatResponse(
            conversation_id=conversation_id,
            message=ai_response,
            recommendations=recommendations
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{user_id}", response_model=ConversationHistoryResponse)
async def get_conversations(
    user_id: str,
    storage: ConversationStorageDep
):
    """
    ユーザーの会話履歴を取得
    """
    try:
        conversations = storage.get_user_conversations(user_id)
        return ConversationHistoryResponse(conversations=conversations)

    except StorageError as e:
        logger.error(f"Storage error getting conversations: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{user_id}/{conversation_id}")
async def delete_conversation(
    user_id: str,
    conversation_id: str,
    storage: ConversationStorageDep
):
    """
    会話を削除
    """
    try:
        success = storage.delete_conversation(user_id, conversation_id)

        if not success:
            raise NotFoundError("Conversation not found")

        return {"message": "Conversation deleted successfully"}

    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except StorageError as e:
        logger.error(f"Storage error deleting conversation: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ExtractPreferencesRequest(BaseModel):
    user_id: str
    conversation_id: str


class ExtractPreferencesResponse(BaseModel):
    preferences: Dict[str, Any]
    recommendations: List[Dict[str, Any]]


@router.post("/extract-preferences", response_model=ExtractPreferencesResponse)
async def extract_preferences(
    request: ExtractPreferencesRequest,
    openai_service: OpenAIServiceDep,
    storage: ConversationStorageDep,
    settings: SettingsDep
):
    """
    会話から条件を抽出し、求人を検索
    """
    try:

        # 会話履歴を読み込み
        conversation_data = storage.load_conversation(
            request.user_id,
            request.conversation_id
        )

        if not conversation_data:
            raise NotFoundError("Conversation not found")

        messages = conversation_data.get("messages", [])

        # 条件を抽出
        preferences = openai_service.extract_job_preferences(messages)

        # 求人を検索
        recommendations = await _search_jobs_by_preferences(
            openai_service,
            storage,
            request.user_id,
            preferences
        )

        return ExtractPreferencesResponse(
            preferences=preferences,
            recommendations=recommendations
        )

    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except (OpenAIError, StorageError) as e:
        logger.error(f"Service error extracting preferences: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error extracting preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _extract_and_search_jobs(
    openai_service,
    storage,
    user_id: str,
    messages: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    """会話から条件を抽出して求人を検索"""
    try:
        # 条件を抽出
        preferences = openai_service.extract_job_preferences(messages)

        # 求人を検索
        return await _search_jobs_by_preferences(
            openai_service,
            storage,
            user_id,
            preferences
        )

    except Exception as e:
        logger.error(f"Error in _extract_and_search_jobs: {e}")
        return []


async def _search_jobs_by_preferences(
    openai_service,
    storage,
    user_id: str,
    preferences: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """条件に基づいて求人を検索"""
    try:
        from app.services.vector_search import VectorSearchService

        # 検索クエリのエンベディングを作成
        query_embedding = openai_service.create_search_query_embedding(preferences)

        # すべての求人エンベディングを取得
        job_embeddings = storage.get_all_job_embeddings()

        if not job_embeddings:
            logger.warning("No job embeddings found. Initializing job embeddings...")
            await _initialize_job_embeddings(openai_service, storage)
            job_embeddings = storage.get_all_job_embeddings()

        # 求人データを読み込み
        job_data_list = _load_job_data()

        # ベクトル検索
        vector_search = VectorSearchService()
        results = vector_search.weighted_search(
            query_embedding=query_embedding,
            job_embeddings=job_embeddings,
            job_data_list=job_data_list,
            preferences=preferences,
            top_k=10
        )

        return results

    except Exception as e:
        logger.error(f"Error in _search_jobs_by_preferences: {e}")
        return []


async def _initialize_job_embeddings(openai_service, storage):
    """求人エンベディングを初期化"""
    try:
        from app.services.vector_search import VectorSearchService

        job_data_list = _load_job_data()

        for job in job_data_list:
            # エンベディング用テキストを作成
            text = VectorSearchService.create_job_embedding_text(job)

            # エンベディングを生成
            embedding = openai_service.create_embedding(text)

            # 保存
            storage.save_job_embedding(
                job_id=job["id"],
                embedding=embedding,
                text=text
            )

        logger.info(f"Initialized embeddings for {len(job_data_list)} jobs")

    except Exception as e:
        logger.error(f"Error initializing job embeddings: {e}")


def _load_job_data() -> List[Dict[str, Any]]:
    """求人データを読み込み"""
    try:
        data_file = Path("data/jobs.json")

        if not data_file.exists():
            logger.warning("jobs.json not found")
            return []

        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("jobs", [])

    except Exception as e:
        logger.error(f"Error loading job data: {e}")
        return []
