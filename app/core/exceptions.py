# app/core/exceptions.py
"""
カスタム例外クラス
"""
from typing import Any, Optional


class JobMatchingException(Exception):
    """ベースとなるカスタム例外"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class ConfigurationError(JobMatchingException):
    """設定エラー"""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, status_code=500, details=details)


class ServiceError(JobMatchingException):
    """サービスレイヤーのエラー"""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, status_code=500, details=details)


class MatchingError(ServiceError):
    """マッチング処理のエラー"""
    pass


class EmbeddingError(ServiceError):
    """エンベディング処理のエラー"""
    pass


class OpenAIError(ServiceError):
    """OpenAI API関連のエラー"""
    pass


class StorageError(ServiceError):
    """ストレージ関連のエラー"""
    pass


class ValidationError(JobMatchingException):
    """バリデーションエラー"""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, status_code=422, details=details)


class NotFoundError(JobMatchingException):
    """リソースが見つからないエラー"""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, status_code=404, details=details)
