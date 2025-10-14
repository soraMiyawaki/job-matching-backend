# main.py
"""
FastAPIアプリケーションのエントリーポイント
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import JobMatchingException
from app.api.endpoints import matching, conversation

# 環境変数を読み込む
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    # 起動時の処理
    logger = get_logger(__name__)
    logger.info("Application startup")

    # 設定の検証
    settings = get_settings()
    logger.info(f"Loaded configuration: {settings.app_name} v{settings.app_version}")

    yield

    # 終了時の処理
    logger.info("Application shutdown")


def create_application() -> FastAPI:
    """
    FastAPIアプリケーションファクトリ

    Returns:
        設定済みのFastAPIアプリケーション
    """
    settings = get_settings()

    # ロギング設定
    setup_logging(settings.log_level)
    logger = get_logger(__name__)

    # FastAPIアプリケーション作成
    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        lifespan=lifespan,
        debug=settings.debug
    )

    # CORS設定
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )

    # グローバル例外ハンドラー
    @app.exception_handler(JobMatchingException)
    async def job_matching_exception_handler(
        request: Request,
        exc: JobMatchingException
    ):
        """カスタム例外のハンドラー"""
        logger.error(
            f"JobMatchingException: {exc.message}",
            extra={"details": exc.details, "path": request.url.path}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "details": exc.details,
                "type": exc.__class__.__name__
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """一般的な例外のハンドラー"""
        logger.error(
            f"Unhandled exception: {str(exc)}",
            exc_info=True,
            extra={"path": request.url.path}
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "message": str(exc) if settings.debug else "An unexpected error occurred"
            }
        )

    # ルーター登録
    app.include_router(
        matching.router,
        prefix="/api/matching",
        tags=["matching"]
    )

    app.include_router(
        conversation.router,
        prefix="/api/conversation",
        tags=["conversation"]
    )

    # ヘルスチェックエンドポイント
    @app.get("/", tags=["health"])
    async def root():
        """ルートエンドポイント"""
        return {
            "message": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health"
        }

    @app.get("/health", tags=["health"])
    async def health():
        """ヘルスチェック"""
        return {
            "status": "healthy",
            "version": settings.app_version
        }

    logger.info(f"Application created successfully: {settings.app_name}")
    return app


# アプリケーションインスタンスを作成
app = create_application()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
