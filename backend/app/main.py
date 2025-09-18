"""RAG Chat API メインアプリケーション

2つのデータベースを使い分けるハイブリッド型RAGアプリケーションです。

データベース構成:
    - PostgreSQL: RDB（リレーショナルDB）- ユーザー情報、構造化データの管理
    - ChromaDB: ベクトルDB - 文書の埋め込みベクトル、セマンティック検索

このモジュールでは、アプリケーションの初期設定とルーター登録を行います。

主な技術スタック:
    - FastAPI: Web フレームワーク
    - PostgreSQL + SQLAlchemy: 構造化データ管理（ユーザー、メタデータ）
    - ChromaDB: ベクトル検索・RAG機能
    - SentenceTransformer: 多言語ベクトル化
    - Pydantic: データバリデーション

Typical usage example:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .config.logging import setup_logging
from .config.database import create_tables
from .routers import health, documents, users, auth, groups

# ログ設定の初期化
setup_logging()

# FastAPIアプリケーションの作成
app = FastAPI(
    title=settings.app_name,
    description="PostgreSQL（RDB）とChromaDB（ベクトルDB）を使い分けるハイブリッド型RAGアプリケーション",
    version=settings.app_version,
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では具体的なオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の処理

    データベーステーブルの作成を行います。
    """
    # データベーステーブルの作成
    create_tables()


# ルーターの登録
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(groups.router)
