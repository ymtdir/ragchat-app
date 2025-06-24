"""RAG Chat API メインアプリケーション

ベクトル検索機能を持つRAG（Retrieval-Augmented Generation）アプリケーションの
FastAPI実装です。

このモジュールでは、以下の機能を提供します:
    - 文書のベクトル化と保存
    - ベクトル類似度検索
    - 文書のCRUD操作
    - コレクション情報の取得

主な技術スタック:
    - FastAPI: Web フレームワーク
    - ChromaDB: ベクトルデータベース
    - SentenceTransformer: 多言語ベクトル化
    - Pydantic: データバリデーション

Typical usage example:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .services.vector import VectorService, get_vector_service
from .schemas.vector import (
    AddDocumentRequest,
    AddDocumentResponse,
    SearchDocumentsRequest,
    SearchDocumentsResponse,
    GetAllDocumentsResponse,
    CollectionInfoResponse,
    DeleteAllDocumentsResponse,
    DeleteDocumentResponse,
    GetDocumentResponse,
)
from .config import settings
import datetime

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


@app.get("/")
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


@app.post("/api/documents", response_model=AddDocumentResponse)
async def add_document(
    request: AddDocumentRequest,
    vector_service: VectorService = Depends(get_vector_service),
) -> AddDocumentResponse:
    """文書をベクトル化してDBに保存

    受け取った文書をベクトル化し、ChromaDBに保存します。
    同じIDが存在する場合は上書きされます。

    Args:
        request: 文書追加リクエスト（id、title、textを含む）
        vector_service: DIで注入されるベクトル化サービス

    Returns:
        AddDocumentResponse: 生成されたベクトル（埋め込み）を含む保存結果

    Raises:
        HTTPException: 文書の保存に失敗した場合（500エラー）

    Example:
        POST /api/documents
        {
            "id": "doc_001",
            "title": "サンプル文書",
            "text": "これはサンプル文書です。"
        }
    """
    print(f"[{datetime.datetime.now()}] 文書追加処理開始")
    try:
        # ベクトル化サービスを使用して文書を保存
        result = await vector_service.add_document(
            id=request.id, title=request.title, text=request.text
        )

        print(f"[{datetime.datetime.now()}] 文書追加処理完了: {result['vector_id']}")

        return AddDocumentResponse(embedding=result["embedding"])

    except Exception as e:
        # エラーが発生した場合は500エラーを返す
        return JSONResponse(
            status_code=500, content={"error": f"文書の保存に失敗しました: {str(e)}"}
        )


@app.post("/api/documents/search", response_model=SearchDocumentsResponse)
async def search_documents(
    request: SearchDocumentsRequest,
    vector_service: VectorService = Depends(get_vector_service),
) -> SearchDocumentsResponse:
    """類似文書を検索

    クエリに類似した文書をベクトルDBから検索します。
    コサイン類似度を使用して最も類似した文書を返します。

    Args:
        request: 検索リクエスト（クエリと取得件数を含む）
        vector_service: DIで注入されるベクトル化サービス

    Returns:
        SearchDocumentsResponse: 類似度順にソートされた検索結果

    Raises:
        HTTPException: 検索処理に失敗した場合（500エラー）

    Example:
        POST /api/documents/search
        {
            "query": "機械学習について",
            "n_results": 5
        }
    """
    print(f"[{datetime.datetime.now()}] 文書検索処理開始")
    try:
        # ベクトル類似度検索を実行
        results = await vector_service.search_similar_documents(
            query=request.query, n_results=request.n_results
        )

        print(f"[{datetime.datetime.now()}] 文書検索処理完了: {len(results)}件")

        return SearchDocumentsResponse(results=results)

    except Exception as e:
        # エラーが発生した場合は500エラーを返す
        return JSONResponse(
            status_code=500, content={"error": f"文書の検索に失敗しました: {str(e)}"}
        )


@app.get("/api/documents", response_model=GetAllDocumentsResponse)
async def get_all_documents(
    vector_service: VectorService = Depends(get_vector_service),
) -> GetAllDocumentsResponse:
    """保存されている全ての文書を取得

    ChromaDBに保存されている全文書を取得します。
    大量のデータが存在する場合はパフォーマンスに注意が必要です。

    Args:
        vector_service: DIで注入されるベクトル化サービス

    Returns:
        GetAllDocumentsResponse: 全文書のリストと総数

    Raises:
        HTTPException: 取得処理に失敗した場合（500エラー）

    Example:
        GET /api/documents
        Response: {
            "documents": [...],
            "count": 10
        }
    """
    try:
        # 全文書を取得
        documents = await vector_service.get_all_documents()
        return GetAllDocumentsResponse(documents=documents, count=len(documents))
    except Exception as e:
        # エラーが発生した場合は500エラーを返す
        return JSONResponse(
            status_code=500, content={"error": f"文書の取得に失敗しました: {str(e)}"}
        )


@app.get("/api/documents/info", response_model=CollectionInfoResponse)
async def get_collection_info(
    vector_service: VectorService = Depends(get_vector_service),
) -> CollectionInfoResponse:
    """コレクションの情報を取得

    ChromaDBコレクションの基本情報（名前、文書数、ストレージ情報）を取得します。
    システムの状態確認やデバッグに使用できます。

    Args:
        vector_service: DIで注入されるベクトル化サービス

    Returns:
        CollectionInfoResponse: コレクションの基本情報

    Raises:
        HTTPException: 情報取得に失敗した場合（500エラー）

    Example:
        GET /api/documents/info
        Response: {
            "collection_name": "documents",
            "document_count": 10,
            "storage_type": "local_persistent",
            "path": "./vector_db"
        }
    """
    try:
        # コレクション情報を取得
        info = await vector_service.get_collection_info()
        return CollectionInfoResponse(**info)
    except Exception as e:
        # エラーが発生した場合は500エラーを返す
        return JSONResponse(
            status_code=500, content={"error": f"情報の取得に失敗しました: {str(e)}"}
        )


@app.delete("/api/documents", response_model=DeleteAllDocumentsResponse)
async def delete_all_documents(
    vector_service: VectorService = Depends(get_vector_service),
) -> DeleteAllDocumentsResponse:
    """保存されている全ての文書を削除

    ChromaDBコレクション内の全文書を削除します。
    この操作は元に戻せないため、本番環境での使用は注意が必要です。

    Args:
        vector_service: DIで注入されるベクトル化サービス

    Returns:
        DeleteAllDocumentsResponse: 削除結果（成功フラグ、削除数、メッセージ）

    Raises:
        HTTPException: 削除処理に失敗した場合（500エラー）

    Warning:
        この操作は元に戻せません。本番環境での使用は注意してください。

    Example:
        DELETE /api/documents
        Response: {
            "success": true,
            "deleted_count": 10,
            "message": "10件の文書を削除しました"
        }
    """
    try:
        print(f"[{datetime.datetime.now()}] 全文書削除処理開始")

        # 全文書を削除
        result = await vector_service.delete_all_documents()

        print(
            f"[{datetime.datetime.now()}] 全文書削除処理完了: {result['deleted_count']}件削除"
        )

        return DeleteAllDocumentsResponse(
            success=result["success"],
            deleted_count=result["deleted_count"],
            message=f"{result['deleted_count']}件の文書を削除しました",
        )
    except Exception as e:
        # エラーが発生した場合は500エラーを返す
        return JSONResponse(
            status_code=500, content={"error": f"全文書の削除に失敗しました: {str(e)}"}
        )


@app.delete("/api/documents/{document_id}", response_model=DeleteDocumentResponse)
async def delete_document(
    document_id: str, vector_service: VectorService = Depends(get_vector_service)
) -> DeleteDocumentResponse:
    """指定されたIDの文書を削除

    ChromaDBから指定されたIDの文書を削除します。
    存在しないIDを指定した場合でもエラーにはなりません。

    Args:
        document_id: 削除する文書の一意識別子
        vector_service: DIで注入されるベクトル化サービス

    Returns:
        DeleteDocumentResponse: 削除結果（成功フラグとメッセージ）

    Raises:
        HTTPException: 削除処理に失敗した場合（500エラー）

    Example:
        DELETE /api/documents/doc_001
        Response: {
            "success": true,
            "message": "文書が正常に削除されました"
        }
    """
    try:
        # 指定されたIDの文書を削除
        success = await vector_service.delete_document(document_id)
        return DeleteDocumentResponse(
            success=success, message="文書が正常に削除されました"
        )
    except Exception as e:
        # エラーが発生した場合は500エラーを返す
        return JSONResponse(
            status_code=500, content={"error": f"文書の削除に失敗しました: {str(e)}"}
        )


@app.get("/api/documents/{document_id}", response_model=GetDocumentResponse)
async def get_document(
    document_id: str,
    vector_service: VectorService = Depends(get_vector_service),
) -> GetDocumentResponse:
    """指定されたIDの文書を取得

    ChromaDBから指定されたIDの文書を取得します。
    文書が存在しない場合は404エラーを返します。

    Args:
        document_id: 取得する文書の一意識別子
        vector_service: DIで注入されるベクトル化サービス

    Returns:
        GetDocumentResponse: 文書の詳細情報

    Raises:
        HTTPException: 文書が見つからない場合（404エラー）、
        その他の取得エラーの場合（500エラー）

    Example:
        GET /api/documents/doc_001
        Response: {
            "id": "doc_001",
            "title": "サンプル文書",
            "text": "これはサンプル文書です。",
            "embedding": null
        }
    """
    try:
        # 指定されたIDの文書を取得
        document = await vector_service.get_document(document_id)
        return GetDocumentResponse(**document)
    except Exception as e:
        # 文書が見つからない場合は404エラーを返す
        return JSONResponse(
            status_code=404, content={"error": f"文書が見つかりません: {str(e)}"}
        )
