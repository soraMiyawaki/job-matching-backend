# app/core/logging.py
"""
ロギング設定
"""
import logging
import sys
from pathlib import Path
from typing import Optional

from app.core.config import get_settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    ロギングシステムをセットアップ

    Args:
        log_level: ログレベル（指定しない場合は設定から取得）
    """
    settings = get_settings()
    level = log_level or settings.log_level

    # ルートロガーの設定
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=settings.log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )

    # サードパーティライブラリのログレベルを調整
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {level}")


def get_logger(name: str) -> logging.Logger:
    """
    名前付きロガーを取得

    Args:
        name: ロガー名

    Returns:
        設定済みのロガー
    """
    return logging.getLogger(name)
