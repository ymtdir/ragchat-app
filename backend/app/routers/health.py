"""
ヘルスチェックルーター

APIの稼働状況を確認するためのエンドポイントを定義します。
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    """ルートエンドポイント

    APIの稼働状況を確認するためのヘルスチェックエンドポイントです。

    Returns:
        dict: APIの稼働状況を示すメッセージ

    Example:
        GET /
        Response: {"message": "RAG Chat API is running"}
    """
    return {"message": "RAG Chat API is running"}
