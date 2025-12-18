"""
Database engine management.
Provides a shared SQLAlchemy engine and simple health check utility.
"""
from functools import lru_cache
from typing import Dict

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Create or return the shared SQLAlchemy engine."""
    settings = get_settings()
    connect_args = {}
    database_url = settings.database_url

    if settings.database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    elif settings.database_url.startswith("postgresql") and "sslmode=" not in settings.database_url.lower():
        separator = "&" if "?" in settings.database_url else "?"
        database_url = f"{settings.database_url}{separator}sslmode=require"

    return create_engine(
        database_url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )


def healthcheck() -> Dict[str, str]:
    """
    Perform a lightweight database health check.
    Returns a dict describing the outcome; callers should handle exceptions.
    """
    engine = get_engine()

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {"status": "ok"}
