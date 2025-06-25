"""RAG Chat API メインアプリケーション

ベクトル検索機能を持つRAG（Retrieval-Augmented Generation）アプリケーションの
FastAPI実装です。

このモジュールでは、アプリケーションの初期設定とルーター登録を行います。

主な技術スタック:
    - FastAPI: Web フレームワーク
    - ChromaDB: ベクトルデータベース
    - SentenceTransformer: 多言語ベクトル化
    - Pydantic: データバリデーション

Typical usage example:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .config.logging import setup_logging
from .routers import health, documents

# ログ設定の初期化
setup_logging()

# FastAPIアプリケーションの作成
app = FastAPI(
    title=settings.app_name,
    description="ベクトル検索機能を持つシンプルなRAGアプリケーション",
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

# ルーターの登録
app.include_router(health.router)
app.include_router(documents.router)
