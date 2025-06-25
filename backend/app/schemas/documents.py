"""
文書管理機能APIスキーマ

文書の追加と検索のためのリクエスト・レスポンスモデルを定義します。

このモジュールでは、FastAPIのPydanticモデルを使用して、
文書管理機能に関するAPIの入力と出力のスキーマを定義しています。

Typical usage example:
    request = AddDocumentRequest(
        id="doc_001",
        title="サンプル文書",
        text="これはサンプル文書です。"
    )
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# ===== Request Schemas =====


class AddDocumentRequest(BaseModel):
    """文書追加リクエストモデル

    文書をベクトルDBに追加するためのリクエストデータを定義します。

    Attributes:
        id: 文書の一意識別子
        title: 文書のタイトル
        text: ベクトル化対象のテキスト内容
    """

    id: str = Field(..., description="文書の一意ID", example="vector-000")
    title: str = Field(..., description="文書のタイトル", example="重要な文書")
    text: str = Field(
        ..., description="ベクトル化するテキスト", example="これは重要な文書です。"
    )


class SearchDocumentsRequest(BaseModel):
    """文書検索リクエストモデル

    ベクトルDBから類似文書を検索するためのリクエストデータを定義します。

    Attributes:
        query: 検索クエリ文字列
        n_results: 取得する検索結果の最大数
    """

    query: str = Field(..., description="検索クエリ", example="使用方法について")
    n_results: int = Field(5, description="取得する結果数", example=5)


# ===== Response Schemas =====


class AddDocumentResponse(BaseModel):
    """文書追加レスポンスモデル

    文書追加処理の結果を返すレスポンスデータを定義します。

    Attributes:
        embedding: 文書から生成されたベクトル（特徴量）
    """

    embedding: List[float] = Field(..., description="テキストの特徴量（ベクトル）")


class SearchResult(BaseModel):
    """検索結果アイテムスキーマ

    検索結果の個別アイテムを表すデータモデルです。

    Attributes:
        id: 文書の一意識別子
        title: 文書のタイトル
        text: 文書の内容
        similarity_score: クエリとの類似度スコア（0.0-1.0）
    """

    id: str = Field(..., description="文書ID")
    title: str = Field(..., description="文書タイトル")
    text: str = Field(..., description="文書内容")
    similarity_score: float = Field(..., ge=0, le=1, description="類似度スコア")


class SearchDocumentsResponse(BaseModel):
    """文書検索レスポンスモデル

    文書検索処理の結果を返すレスポンスデータを定義します。

    Attributes:
        results: 検索結果のリスト
    """

    results: List[SearchResult] = Field(..., description="検索結果")


class GetAllDocumentsResponse(BaseModel):
    """全文書取得レスポンスモデル

    保存されている全文書を取得した結果を返すレスポンスデータです。

    Attributes:
        documents: 全文書のリスト
        count: 文書の総数
    """

    documents: List[SearchResult] = Field(..., description="全文書のリスト")
    count: int = Field(..., description="文書の総数")


class CollectionInfoResponse(BaseModel):
    """コレクション情報レスポンスモデル

    ベクトルDBのコレクション情報を返すレスポンスデータです。

    Attributes:
        collection_name: コレクションの名前
        document_count: 保存されている文書数
        storage_type: ストレージの種類
        path: ストレージのパス
    """

    collection_name: str = Field(..., description="コレクション名")
    document_count: int = Field(..., description="文書の総数")
    storage_type: str = Field(..., description="ストレージタイプ")
    path: str = Field(..., description="ストレージパス")


class DeleteDocumentRequest(BaseModel):
    """文書削除リクエストモデル

    特定の文書を削除するためのリクエストデータを定義します。

    Attributes:
        document_id: 削除対象の文書ID
    """

    document_id: str = Field(..., description="削除する文書のID")


class DeleteDocumentResponse(BaseModel):
    """文書削除レスポンスモデル

    文書削除処理の結果を返すレスポンスデータを定義します。

    Attributes:
        success: 削除処理の成功フラグ
        message: 処理結果メッセージ
    """

    success: bool = Field(..., description="削除成功フラグ")
    message: str = Field(..., description="処理結果メッセージ")


class DeleteAllDocumentsResponse(BaseModel):
    """全文書削除レスポンスモデル

    全文書削除処理の結果を返すレスポンスデータを定義します。

    Attributes:
        success: 削除処理の成功フラグ
        deleted_count: 削除された文書数
        message: 処理結果メッセージ
    """

    success: bool = Field(..., description="削除成功フラグ")
    deleted_count: int = Field(..., description="削除された文書数")
    message: str = Field(..., description="処理結果メッセージ")


class GetDocumentResponse(BaseModel):
    """個別文書取得レスポンスモデル

    特定の文書を取得した結果を返すレスポンスデータを定義します。

    Attributes:
        id: 文書の一意識別子
        title: 文書のタイトル
        text: 文書の内容
        embedding: 文書の埋め込みベクトル（オプショナル）
    """

    id: str = Field(..., description="文書のID")
    title: str = Field(..., description="文書のタイトル")
    text: str = Field(..., description="文書の内容")
    embedding: Optional[List[float]] = Field(None, description="埋め込みベクトル")
