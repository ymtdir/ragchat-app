"""
文書管理ルーター

文書のCRUD操作とベクトル検索機能を提供するエンドポイントを定義します。

このモジュールでは、以下の機能を提供します:
    - 文書の追加・削除・取得
    - ベクトル類似度検索
    - コレクション情報の取得
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from ..services.documents import DocumentService, get_documents_service
from ..schemas.documents import (
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
from ..config.logging import get_logger

logger = get_logger(__name__)

# 文書管理用ルーターの作成
router = APIRouter(
    prefix="/api/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=AddDocumentResponse)
async def add_document(
    request: AddDocumentRequest,
    document_service: DocumentService = Depends(get_documents_service),
) -> AddDocumentResponse:
    """文書をベクトル化してDBに保存

    受け取った文書をベクトル化し、ChromaDBに保存します。
    同じIDが存在する場合は上書きされます。

    Args:
        request: 文書追加リクエスト（id、title、textを含む）
        document_service: DIで注入される文書管理サービス

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
    logger.info("文書追加処理開始")
    try:
        # 文書管理サービスを使用して文書を保存
        result = await document_service.add_document(
            id=request.id, title=request.title, text=request.text
        )

        logger.info(f"文書追加処理完了: {result['vector_id']}")

        return AddDocumentResponse(embedding=result["embedding"])

    except Exception as e:
        # エラーが発生した場合は500エラーを返す
        return JSONResponse(
            status_code=500, content={"error": f"文書の保存に失敗しました: {str(e)}"}
        )


@router.post("/search", response_model=SearchDocumentsResponse)
async def search_documents(
    request: SearchDocumentsRequest,
    document_service: DocumentService = Depends(get_documents_service),
) -> SearchDocumentsResponse:
    """類似文書を検索

    クエリに類似した文書をベクトルDBから検索します。
    コサイン類似度を使用して最も類似した文書を返します。

    Args:
        request: 検索リクエスト（クエリと取得件数を含む）
        document_service: DIで注入される文書管理サービス

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
    logger.info("文書検索処理開始")
    try:
        # ベクトル類似度検索を実行
        results = await document_service.search_similar_documents(
            query=request.query, n_results=request.n_results
        )

        logger.info(f"文書検索処理完了: {len(results)}件")

        return SearchDocumentsResponse(results=results)

    except Exception as e:
        # エラーが発生した場合は500エラーを返す
        return JSONResponse(
            status_code=500, content={"error": f"文書の検索に失敗しました: {str(e)}"}
        )


@router.get("/", response_model=GetAllDocumentsResponse)
async def get_all_documents(
    document_service: DocumentService = Depends(get_documents_service),
) -> GetAllDocumentsResponse:
    """保存されている全ての文書を取得

    ChromaDBに保存されている全文書を取得します。
    大量のデータが存在する場合はパフォーマンスに注意が必要です。

    Args:
        document_service: DIで注入される文書管理サービス

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
        documents = await document_service.get_all_documents()
        return GetAllDocumentsResponse(documents=documents, count=len(documents))
    except Exception as e:
        # エラーが発生した場合は500エラーを返す
        return JSONResponse(
            status_code=500, content={"error": f"文書の取得に失敗しました: {str(e)}"}
        )


@router.get("/info", response_model=CollectionInfoResponse)
async def get_collection_info(
    document_service: DocumentService = Depends(get_documents_service),
) -> CollectionInfoResponse:
    """コレクションの情報を取得

    ChromaDBコレクションの基本情報（名前、文書数、ストレージ情報）を取得します。
    システムの状態確認やデバッグに使用できます。

    Args:
        document_service: DIで注入される文書管理サービス

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
        info = await document_service.get_collection_info()
        return CollectionInfoResponse(**info)
    except Exception as e:
        # エラーが発生した場合は500エラーを返す
        return JSONResponse(
            status_code=500, content={"error": f"情報の取得に失敗しました: {str(e)}"}
        )


@router.delete("/", response_model=DeleteAllDocumentsResponse)
async def delete_all_documents(
    document_service: DocumentService = Depends(get_documents_service),
) -> DeleteAllDocumentsResponse:
    """保存されている全ての文書を削除

    ChromaDBコレクション内の全文書を削除します。
    この操作は元に戻せないため、本番環境での使用は注意が必要です。

    Args:
        document_service: DIで注入される文書管理サービス

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
        logger.info("全文書削除処理開始")

        # 全文書を削除
        result = await document_service.delete_all_documents()

        logger.info(f"全文書削除処理完了: {result['deleted_count']}件削除")

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


@router.delete("/{document_id}", response_model=DeleteDocumentResponse)
async def delete_document(
    document_id: str, document_service: DocumentService = Depends(get_documents_service)
) -> DeleteDocumentResponse:
    """指定されたIDの文書を削除

    ChromaDBから指定されたIDの文書を削除します。
    存在しないIDを指定した場合でもエラーにはなりません。

    Args:
        document_id: 削除する文書の一意識別子
        document_service: DIで注入される文書管理サービス

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
        success = await document_service.delete_document(document_id)
        return DeleteDocumentResponse(
            success=success, message="文書が正常に削除されました"
        )
    except Exception as e:
        # エラーが発生した場合は500エラーを返す
        return JSONResponse(
            status_code=500, content={"error": f"文書の削除に失敗しました: {str(e)}"}
        )


@router.get("/{document_id}", response_model=GetDocumentResponse)
async def get_document(
    document_id: str,
    document_service: DocumentService = Depends(get_documents_service),
) -> GetDocumentResponse:
    """指定されたIDの文書を取得

    ChromaDBから指定されたIDの文書を取得します。
    文書が存在しない場合は404エラーを返します。

    Args:
        document_id: 取得する文書の一意識別子
        document_service: DIで注入される文書管理サービス

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
        document = await document_service.get_document(document_id)
        return GetDocumentResponse(**document)
    except Exception as e:
        # 文書が見つからない場合は404エラーを返す
        return JSONResponse(
            status_code=404, content={"error": f"文書が見つかりません: {str(e)}"}
        )
