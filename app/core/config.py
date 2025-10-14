# app/core/config.py
"""
アプリケーション設定管理
Pydantic Settingsを使用して環境変数から設定を読み込む
"""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定"""

    # アプリケーション情報
    app_name: str = "Job Matching API"
    app_version: str = "1.0.0"
    app_description: str = "AI求人マッチングシステムのバックエンドAPI"
    debug: bool = False

    # サーバー設定
    host: str = "127.0.0.1"
    port: int = 8888

    # CORS設定
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",
            "http://localhost:5176",
            "http://localhost:5177",
            "http://localhost:5178",
            "http://localhost:5179",
            "http://localhost:5180",
        ]
    )
    cors_credentials: bool = True
    cors_methods: List[str] = Field(default=["*"])
    cors_headers: List[str] = Field(default=["*"])

    # OpenAI API設定
    openai_api_key: str = Field(..., description="OpenAI API Key")
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_dimension: int = 1536

    # データベース設定（将来の拡張用）
    database_url: str = Field(
        default="sqlite:///./job_matching.db",
        description="Database connection URL"
    )

    # ファイルストレージ設定
    data_directory: str = "./data"
    conversations_directory: str = "./data/conversations"
    embeddings_directory: str = "./data/embeddings"
    jobs_file: str = "./data/jobs.json"

    # ロギング設定
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # マッチング設定
    default_top_k: int = 10
    matching_threshold: float = 0.5

    # セキュリティ設定（将来の拡張用）
    secret_key: str = Field(
        default="your-secret-key-here",
        description="Secret key for JWT tokens"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# シングルトンインスタンス
_settings: Settings | None = None


def get_settings() -> Settings:
    """設定のシングルトンインスタンスを取得"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
