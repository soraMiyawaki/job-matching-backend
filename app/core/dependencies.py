# app/core/dependencies.py
"""
FastAPI依存性注入
全アプリケーションで使用される依存関数を定義
"""
from typing import Annotated
from fastapi import Depends

from app.core.config import Settings, get_settings
from app.services.openai_service import OpenAIService
from app.services.conversation_storage import ConversationStorage
from app.services.vector_search import VectorSearchService
from app.ml.embedding_service import EmbeddingService
from app.ml.matching_service import MatchingService
from app.ml.conversation_service import ConversationService


# 設定
def get_settings_dependency() -> Settings:
    """設定を取得"""
    return get_settings()


# サービス層のシングルトンインスタンス
_openai_service: OpenAIService | None = None
_conversation_storage: ConversationStorage | None = None
_vector_search_service: VectorSearchService | None = None


def get_openai_service(
    settings: Annotated[Settings, Depends(get_settings_dependency)]
) -> OpenAIService:
    """OpenAIServiceのシングルトンインスタンスを取得"""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService(settings)
    return _openai_service


def get_conversation_storage(
    settings: Annotated[Settings, Depends(get_settings_dependency)]
) -> ConversationStorage:
    """ConversationStorageのシングルトンインスタンスを取得"""
    global _conversation_storage
    if _conversation_storage is None:
        _conversation_storage = ConversationStorage(settings)
    return _conversation_storage


def get_vector_search_service() -> VectorSearchService:
    """VectorSearchServiceのシングルトンインスタンスを取得"""
    global _vector_search_service
    if _vector_search_service is None:
        _vector_search_service = VectorSearchService()
    return _vector_search_service


# ML層のシングルトンインスタンス
_embedding_service: EmbeddingService | None = None
_matching_service: MatchingService | None = None
_conversation_service: ConversationService | None = None


def get_embedding_service(
    settings: Annotated[Settings, Depends(get_settings_dependency)]
) -> EmbeddingService:
    """EmbeddingServiceのシングルトンインスタンスを取得"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService(
            model_name=settings.openai_embedding_model
        )
    return _embedding_service


def get_matching_service(
    embedding_service: Annotated[EmbeddingService, Depends(get_embedding_service)]
) -> MatchingService:
    """MatchingServiceのシングルトンインスタンスを取得"""
    global _matching_service
    if _matching_service is None:
        _matching_service = MatchingService(embedding_service)
    return _matching_service


def get_conversation_service_dependency(
    openai_service: Annotated[OpenAIService, Depends(get_openai_service)]
) -> ConversationService:
    """ConversationServiceのシングルトンインスタンスを取得"""
    global _conversation_service
    if _conversation_service is None:
        _conversation_service = ConversationService(openai_service)
    return _conversation_service


# 型ヒント用のエイリアス
SettingsDep = Annotated[Settings, Depends(get_settings_dependency)]
OpenAIServiceDep = Annotated[OpenAIService, Depends(get_openai_service)]
ConversationStorageDep = Annotated[ConversationStorage, Depends(get_conversation_storage)]
VectorSearchServiceDep = Annotated[VectorSearchService, Depends(get_vector_search_service)]
EmbeddingServiceDep = Annotated[EmbeddingService, Depends(get_embedding_service)]
MatchingServiceDep = Annotated[MatchingService, Depends(get_matching_service)]
ConversationServiceDep = Annotated[ConversationService, Depends(get_conversation_service_dependency)]
