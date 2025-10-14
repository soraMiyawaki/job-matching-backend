# app/services/conversation_storage.py
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
from pathlib import Path

from app.core.config import Settings
from app.core.exceptions import StorageError

logger = logging.getLogger(__name__)


class ConversationStorage:
    """会話履歴とエンベディングを管理するストレージ"""

    def __init__(self, settings: Settings):
        """
        Args:
            settings: アプリケーション設定
        """
        self.data_dir = Path(settings.data_directory)
        self.conversations_dir = Path(settings.conversations_directory)
        self.embeddings_dir = Path(settings.embeddings_directory)
        self.user_profiles_dir = self.data_dir / "user_profiles"

        # ディレクトリを作成
        try:
            self.conversations_dir.mkdir(parents=True, exist_ok=True)
            self.embeddings_dir.mkdir(parents=True, exist_ok=True)
            self.user_profiles_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise StorageError(f"Failed to create storage directories: {str(e)}")

    def save_conversation(
        self,
        user_id: str,
        conversation_id: str,
        messages: List[Dict[str, str]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        会話を保存

        Args:
            user_id: ユーザーID
            conversation_id: 会話ID
            messages: メッセージのリスト
            metadata: メタデータ
        """
        try:
            conversation_data = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "messages": messages,
                "metadata": metadata or {},
                "created_at": metadata.get("created_at") if metadata else datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            file_path = self.conversations_dir / f"{user_id}_{conversation_id}.json"

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)

            logger.debug(f"Saved conversation {conversation_id} for user {user_id}")

        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            raise

    def load_conversation(
        self,
        user_id: str,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        会話を読み込み

        Args:
            user_id: ユーザーID
            conversation_id: 会話ID

        Returns:
            会話データ、存在しない場合はNone
        """
        try:
            file_path = self.conversations_dir / f"{user_id}_{conversation_id}.json"

            if not file_path.exists():
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Error loading conversation: {e}")
            return None

    def get_user_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        ユーザーのすべての会話を取得

        Args:
            user_id: ユーザーID

        Returns:
            会話データのリスト
        """
        try:
            conversations = []
            pattern = f"{user_id}_*.json"

            for file_path in self.conversations_dir.glob(pattern):
                with open(file_path, 'r', encoding='utf-8') as f:
                    conversations.append(json.load(f))

            # 更新日時で降順ソート
            conversations.sort(
                key=lambda x: x.get("updated_at", ""),
                reverse=True
            )

            return conversations

        except Exception as e:
            logger.error(f"Error getting user conversations: {e}")
            return []

    def delete_conversation(self, user_id: str, conversation_id: str) -> bool:
        """
        会話を削除

        Args:
            user_id: ユーザーID
            conversation_id: 会話ID

        Returns:
            削除成功ならTrue
        """
        try:
            file_path = self.conversations_dir / f"{user_id}_{conversation_id}.json"

            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Deleted conversation {conversation_id} for user {user_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False

    def save_job_embedding(
        self,
        job_id: str,
        embedding: List[float],
        text: str
    ) -> None:
        """
        求人のエンベディングを保存

        Args:
            job_id: 求人ID
            embedding: エンベディングベクトル
            text: エンベディング化したテキスト
        """
        try:
            embedding_data = {
                "job_id": job_id,
                "embedding": embedding,
                "text": text,
                "created_at": datetime.now().isoformat()
            }

            file_path = self.embeddings_dir / f"job_{job_id}.json"

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(embedding_data, f, ensure_ascii=False, indent=2)

            logger.debug(f"Saved embedding for job {job_id}")

        except Exception as e:
            logger.error(f"Error saving job embedding: {e}")
            raise

    def load_job_embedding(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        求人のエンベディングを読み込み

        Args:
            job_id: 求人ID

        Returns:
            エンベディングデータ、存在しない場合はNone
        """
        try:
            file_path = self.embeddings_dir / f"job_{job_id}.json"

            if not file_path.exists():
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Error loading job embedding: {e}")
            return None

    def get_all_job_embeddings(self) -> List[Dict[str, Any]]:
        """
        すべての求人エンベディングを取得

        Returns:
            エンベディングデータのリスト
        """
        try:
            embeddings = []
            pattern = "job_*.json"

            for file_path in self.embeddings_dir.glob(pattern):
                with open(file_path, 'r', encoding='utf-8') as f:
                    embeddings.append(json.load(f))

            return embeddings

        except Exception as e:
            logger.error(f"Error getting all job embeddings: {e}")
            return []

    def save_user_profile_embedding(
        self,
        user_id: str,
        embedding: List[float],
        profile_text: str
    ) -> None:
        """
        ユーザープロフィールのエンベディングを保存

        Args:
            user_id: ユーザーID
            embedding: エンベディングベクトル
            profile_text: プロフィールテキスト
        """
        try:
            embedding_data = {
                "user_id": user_id,
                "embedding": embedding,
                "profile_text": profile_text,
                "created_at": datetime.now().isoformat()
            }

            file_path = self.user_profiles_dir / f"{user_id}_embedding.json"

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(embedding_data, f, ensure_ascii=False, indent=2)

            logger.debug(f"Saved profile embedding for user {user_id}")

        except Exception as e:
            logger.error(f"Error saving user profile embedding: {e}")
            raise

    def load_user_profile_embedding(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        ユーザープロフィールのエンベディングを読み込み

        Args:
            user_id: ユーザーID

        Returns:
            エンベディングデータ、存在しない場合はNone
        """
        try:
            file_path = self.user_profiles_dir / f"{user_id}_embedding.json"

            if not file_path.exists():
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Error loading user profile embedding: {e}")
            return None


# 後方互換性のための非推奨関数（依存性注入を使用することを推奨）
_conversation_storage = None


def get_conversation_storage() -> ConversationStorage:
    """
    ConversationStorageのシングルトンインスタンスを取得

    注意: この関数は非推奨です。代わりにFastAPIの依存性注入を使用してください。
    app.core.dependencies.get_conversation_storage を使用することを推奨します。
    """
    global _conversation_storage
    if _conversation_storage is None:
        from app.core.config import get_settings
        settings = get_settings()
        _conversation_storage = ConversationStorage(settings)
    return _conversation_storage
