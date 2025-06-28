"""
文書管理エンドポイントのテストモジュール

テスト実行方法:
1. コマンドラインからの実行:
    python -m pytest -v tests/
    python -m pytest -v tests/test_documents.py

2. 特定のテストメソッドだけ実行:
    python -m pytest -v tests/test_documents.py::test_add_document_success
    python -m pytest -v tests/test_documents.py::test_search_documents_success

3. カバレッジレポート生成:
    coverage run -m pytest tests/
    coverage report
    coverage html
"""

from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.services.documents import get_documents_service


class TestAddDocument:
    """文書追加エンドポイントのテストクラス"""

    def test_add_document_success(self, client: TestClient):
        """文書追加の正常系テスト

        正常な文書データを送信した際に、適切なレスポンスが返されることを検証します。
        """
        # モックサービスの設定
        mock_result = {"vector_id": "doc_001", "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]}

        # DocumentServiceのモックインスタンスを作成
        mock_service_instance = MagicMock()
        mock_service_instance.add_document = AsyncMock(return_value=mock_result)

        # 依存性注入をオーバーライド
        def override_get_documents_service():
            return mock_service_instance

        app.dependency_overrides[get_documents_service] = override_get_documents_service

        try:
            # テストデータ
            request_data = {
                "id": "doc_001",
                "title": "テスト文書",
                "text": "これはテスト用の文書です。",
            }

            # APIリクエストを送信
            response = client.post("/api/documents/", json=request_data)

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert "embedding" in response_data
            assert response_data["embedding"] == mock_result["embedding"]
        finally:
            # オーバーライドをクリア
            app.dependency_overrides.clear()

    def test_add_document_invalid_data(self, client: TestClient):
        """文書追加の異常系テスト（不正なデータ）

        必須フィールドが不足している場合のエラーハンドリングを検証します。
        """
        # 不正なリクエストデータ（idフィールドが不足）
        invalid_request_data = {
            "title": "テスト文書",
            "text": "これはテスト用の文書です。",
        }

        # APIリクエストを送信
        response = client.post("/api/documents/", json=invalid_request_data)

        # バリデーションエラーの検証
        assert response.status_code == 422

    def test_add_document_service_error(self, client: TestClient):
        """文書追加の異常系テスト（サービスエラー）

        文書サービスでエラーが発生した場合のエラーハンドリングを検証します。
        """
        # DocumentServiceのモックインスタンスを作成
        mock_service_instance = MagicMock()
        mock_service_instance.add_document = AsyncMock(
            side_effect=Exception("データベースエラー")
        )

        # 依存性注入をオーバーライド
        def override_get_documents_service():
            return mock_service_instance

        app.dependency_overrides[get_documents_service] = override_get_documents_service

        try:
            # テストデータ
            request_data = {
                "id": "doc_001",
                "title": "テスト文書",
                "text": "これはテスト用の文書です。",
            }

            # APIリクエストを送信
            response = client.post("/api/documents/", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 500
            response_data = response.json()
            assert "error" in response_data
        finally:
            # オーバーライドをクリア
            app.dependency_overrides.clear()


class TestSearchDocuments:
    """文書検索エンドポイントのテストクラス"""

    def test_search_documents_success(self, client: TestClient):
        """文書検索の正常系テスト

        検索クエリに対して適切な検索結果が返されることを検証します。
        """
        # モック検索結果
        mock_results = [
            {
                "id": "doc_001",
                "title": "機械学習入門",
                "text": "機械学習の基本概念について説明します。",
                "similarity_score": 0.95,
            },
            {
                "id": "doc_002",
                "title": "深層学習の応用",
                "text": "深層学習の実用的な応用例を紹介します。",
                "similarity_score": 0.82,
            },
        ]

        # DocumentServiceのモックインスタンスを作成
        mock_service_instance = MagicMock()
        mock_service_instance.search_similar_documents = AsyncMock(
            return_value=mock_results
        )

        # 依存性注入をオーバーライド
        def override_get_documents_service():
            return mock_service_instance

        app.dependency_overrides[get_documents_service] = override_get_documents_service

        try:
            # テストデータ
            request_data = {"query": "機械学習について教えて", "n_results": 5}

            # APIリクエストを送信
            response = client.post("/api/documents/search", json=request_data)

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert "results" in response_data
            assert len(response_data["results"]) == 2
            assert response_data["results"][0]["similarity_score"] == 0.95
        finally:
            # オーバーライドをクリア
            app.dependency_overrides.clear()

    def test_search_documents_invalid_data(self, client: TestClient):
        """文書検索の異常系テスト（不正なデータ）

        必須フィールドが不足している場合のエラーハンドリングを検証します。
        """
        # 不正なリクエストデータ（queryフィールドが不足）
        invalid_request_data = {"n_results": 5}

        # APIリクエストを送信
        response = client.post("/api/documents/search", json=invalid_request_data)

        # バリデーションエラーの検証
        assert response.status_code == 422


class TestGetAllDocuments:
    """全文書取得エンドポイントのテストクラス"""

    def test_get_all_documents_success(self, client: TestClient):
        """全文書取得の正常系テスト

        保存されている全文書が適切に取得できることを検証します。
        """
        # モック文書データ（SearchResultスキーマに合わせてsimilarity_scoreを追加）
        mock_documents = [
            {
                "id": "doc_001",
                "title": "文書1",
                "text": "これは文書1です。",
                "similarity_score": 1.0,
            },
            {
                "id": "doc_002",
                "title": "文書2",
                "text": "これは文書2です。",
                "similarity_score": 1.0,
            },
        ]

        # DocumentServiceのモックインスタンスを作成
        mock_service_instance = MagicMock()
        mock_service_instance.get_all_documents = AsyncMock(return_value=mock_documents)

        # 依存性注入をオーバーライド
        def override_get_documents_service():
            return mock_service_instance

        app.dependency_overrides[get_documents_service] = override_get_documents_service

        try:
            # APIリクエストを送信
            response = client.get("/api/documents/")

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert "documents" in response_data
            assert "count" in response_data
            assert response_data["count"] == 2
            assert len(response_data["documents"]) == 2
        finally:
            # オーバーライドをクリア
            app.dependency_overrides.clear()

    def test_get_all_documents_empty(self, client: TestClient):
        """全文書取得の正常系テスト（空の結果）

        文書が1件もない場合の動作を検証します。
        """
        # DocumentServiceのモックインスタンスを作成
        mock_service_instance = MagicMock()
        mock_service_instance.get_all_documents = AsyncMock(return_value=[])

        # 依存性注入をオーバーライド
        def override_get_documents_service():
            return mock_service_instance

        app.dependency_overrides[get_documents_service] = override_get_documents_service

        try:
            # APIリクエストを送信
            response = client.get("/api/documents/")

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["count"] == 0
            assert response_data["documents"] == []
        finally:
            # オーバーライドをクリア
            app.dependency_overrides.clear()


class TestGetCollectionInfo:
    """コレクション情報取得エンドポイントのテストクラス"""

    def test_get_collection_info_success(self, client: TestClient):
        """コレクション情報取得の正常系テスト

        コレクションの基本情報が適切に取得できることを検証します。
        """
        # モックコレクション情報
        mock_info = {
            "collection_name": "documents",
            "document_count": 10,
            "storage_type": "local_persistent",
            "path": "./vector_db",
        }

        # DocumentServiceのモックインスタンスを作成
        mock_service_instance = MagicMock()
        mock_service_instance.get_collection_info = AsyncMock(return_value=mock_info)

        # 依存性注入をオーバーライド
        def override_get_documents_service():
            return mock_service_instance

        app.dependency_overrides[get_documents_service] = override_get_documents_service

        try:
            # APIリクエストを送信
            response = client.get("/api/documents/info")

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["collection_name"] == "documents"
            assert response_data["document_count"] == 10
            assert response_data["storage_type"] == "local_persistent"
        finally:
            # オーバーライドをクリア
            app.dependency_overrides.clear()


class TestDeleteAllDocuments:
    """全文書削除エンドポイントのテストクラス"""

    def test_delete_all_documents_success(self, client: TestClient):
        """全文書削除の正常系テスト

        全文書が適切に削除されることを検証します。
        """
        # モック削除結果
        mock_result = {"success": True, "deleted_count": 5}

        # DocumentServiceのモックインスタンスを作成
        mock_service_instance = MagicMock()
        mock_service_instance.delete_all_documents = AsyncMock(return_value=mock_result)

        # 依存性注入をオーバーライド
        def override_get_documents_service():
            return mock_service_instance

        app.dependency_overrides[get_documents_service] = override_get_documents_service

        try:
            # APIリクエストを送信
            response = client.delete("/api/documents/")

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] is True
            assert response_data["deleted_count"] == 5
            assert "5件の文書を削除しました" in response_data["message"]
        finally:
            # オーバーライドをクリア
            app.dependency_overrides.clear()

    def test_delete_all_documents_empty(self, client: TestClient):
        """全文書削除の正常系テスト（削除対象なし）

        削除対象がない場合の動作を検証します。
        """
        # モック削除結果（削除対象なし）
        mock_result = {"success": True, "deleted_count": 0}

        # DocumentServiceのモックインスタンスを作成
        mock_service_instance = MagicMock()
        mock_service_instance.delete_all_documents = AsyncMock(return_value=mock_result)

        # 依存性注入をオーバーライド
        def override_get_documents_service():
            return mock_service_instance

        app.dependency_overrides[get_documents_service] = override_get_documents_service

        try:
            # APIリクエストを送信
            response = client.delete("/api/documents/")

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] is True
            assert response_data["deleted_count"] == 0
        finally:
            # オーバーライドをクリア
            app.dependency_overrides.clear()


class TestDeleteDocument:
    """個別文書削除エンドポイントのテストクラス"""

    def test_delete_document_success(self, client: TestClient):
        """個別文書削除の正常系テスト

        指定したIDの文書が適切に削除されることを検証します。
        """
        # DocumentServiceのモックインスタンスを作成
        mock_service_instance = MagicMock()
        mock_service_instance.delete_document = AsyncMock(return_value=True)

        # 依存性注入をオーバーライド
        def override_get_documents_service():
            return mock_service_instance

        app.dependency_overrides[get_documents_service] = override_get_documents_service

        try:
            # APIリクエストを送信
            response = client.delete("/api/documents/doc_001")

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] is True
            assert "文書が正常に削除されました" in response_data["message"]
        finally:
            # オーバーライドをクリア
            app.dependency_overrides.clear()

    def test_delete_document_not_found(self, client: TestClient):
        """個別文書削除のテスト（存在しない文書）

        存在しないIDを指定した場合の動作を検証します。
        """
        # DocumentServiceのモックインスタンスを作成
        mock_service_instance = MagicMock()
        mock_service_instance.delete_document = AsyncMock(return_value=False)

        # 依存性注入をオーバーライド
        def override_get_documents_service():
            return mock_service_instance

        app.dependency_overrides[get_documents_service] = override_get_documents_service

        try:
            # APIリクエストを送信
            response = client.delete("/api/documents/nonexistent_doc")

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] is False
        finally:
            # オーバーライドをクリア
            app.dependency_overrides.clear()


class TestGetDocument:
    """個別文書取得エンドポイントのテストクラス"""

    def test_get_document_success(self, client: TestClient):
        """個別文書取得の正常系テスト

        指定したIDの文書が適切に取得できることを検証します。
        """
        # モック文書データ
        mock_document = {
            "id": "doc_001",
            "title": "テスト文書",
            "text": "これはテスト用の文書です。",
            "embedding": None,
        }

        # DocumentServiceのモックインスタンスを作成
        mock_service_instance = MagicMock()
        mock_service_instance.get_document = AsyncMock(return_value=mock_document)

        # 依存性注入をオーバーライド
        def override_get_documents_service():
            return mock_service_instance

        app.dependency_overrides[get_documents_service] = override_get_documents_service

        try:
            # APIリクエストを送信
            response = client.get("/api/documents/doc_001")

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["id"] == "doc_001"
            assert response_data["title"] == "テスト文書"
            assert response_data["text"] == "これはテスト用の文書です。"
        finally:
            # オーバーライドをクリア
            app.dependency_overrides.clear()

    def test_get_document_not_found(self, client: TestClient):
        """個別文書取得のテスト（存在しない文書）

        存在しないIDを指定した場合のエラーハンドリングを検証します。
        """
        # DocumentServiceのモックインスタンスを作成
        mock_service_instance = MagicMock()
        mock_service_instance.get_document = AsyncMock(
            side_effect=Exception("文書が見つかりません")
        )

        # 依存性注入をオーバーライド
        def override_get_documents_service():
            return mock_service_instance

        app.dependency_overrides[get_documents_service] = override_get_documents_service

        try:
            # APIリクエストを送信
            response = client.get("/api/documents/nonexistent_doc")

            # エラーレスポンスの検証
            assert response.status_code == 404
            response_data = response.json()
            assert "error" in response_data
        finally:
            # オーバーライドをクリア
            app.dependency_overrides.clear()


class TestDocumentsIntegration:
    """文書管理機能の統合テストクラス"""

    def test_document_lifecycle(self, client: TestClient):
        """文書のライフサイクルテスト

        文書の追加→取得→検索→削除の一連の流れをテストします。
        """
        # モックサービスの設定
        mock_add_result = {"vector_id": "doc_001", "embedding": [0.1, 0.2, 0.3]}
        mock_document = {
            "id": "doc_001",
            "title": "ライフサイクルテスト文書",
            "text": "このテストは文書のライフサイクルを確認します。",
            "embedding": None,
        }
        # 検索結果用にsimilarity_scoreを追加
        mock_search_results = [
            {
                "id": "doc_001",
                "title": "ライフサイクルテスト文書",
                "text": "このテストは文書のライフサイクルを確認します。",
                "similarity_score": 0.95,
            }
        ]

        # DocumentServiceのモックインスタンスを作成
        mock_service_instance = MagicMock()
        mock_service_instance.add_document = AsyncMock(return_value=mock_add_result)
        mock_service_instance.get_document = AsyncMock(return_value=mock_document)
        mock_service_instance.search_similar_documents = AsyncMock(
            return_value=mock_search_results
        )
        mock_service_instance.delete_document = AsyncMock(return_value=True)

        # 依存性注入をオーバーライド
        def override_get_documents_service():
            return mock_service_instance

        app.dependency_overrides[get_documents_service] = override_get_documents_service

        try:
            # 1. 文書を追加
            add_request = {
                "id": "doc_001",
                "title": "ライフサイクルテスト文書",
                "text": "このテストは文書のライフサイクルを確認します。",
            }
            add_response = client.post("/api/documents/", json=add_request)
            assert add_response.status_code == 200

            # 2. 文書を取得
            get_response = client.get("/api/documents/doc_001")
            assert get_response.status_code == 200
            assert get_response.json()["id"] == "doc_001"

            # 3. 文書を検索
            search_request = {"query": "ライフサイクル", "n_results": 5}
            search_response = client.post("/api/documents/search", json=search_request)
            assert search_response.status_code == 200
            assert len(search_response.json()["results"]) > 0

            # 4. 文書を削除
            delete_response = client.delete("/api/documents/doc_001")
            assert delete_response.status_code == 200
            assert delete_response.json()["success"] is True
        finally:
            # オーバーライドをクリア
            app.dependency_overrides.clear()
