# init_db.py
"""
データベース初期化スクリプト
"""
from app.db.base import Base
from app.db.session import engine
from app.models import User, Job, Application, Scout

def init_db():
    """
    データベーステーブルを作成
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
