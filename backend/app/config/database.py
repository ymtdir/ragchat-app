"""データベース設定とセッション管理

SQLAlchemyエンジンとセッション管理を提供します。
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from .settings import settings

# SQLAlchemyエンジンの作成
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # デバッグモード時にSQLを出力
    pool_pre_ping=True,  # 接続プールの健全性チェック
    pool_recycle=300,  # 接続を300秒で再利用
)

# セッションファクトリーの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Baseクラス
Base = declarative_base()


def get_db() -> Session:
    """データベースセッションを取得する依存性注入関数

    FastAPIの依存性注入システムで使用します。

    Yields:
        Session: SQLAlchemyセッション
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """テーブルを作成する関数"""
    Base.metadata.create_all(bind=engine)
