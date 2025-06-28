"""
ヘルスチェックエンドポイントのテストモジュール

テスト実行方法:
1. コマンドラインからの実行:
    python -m pytest -v tests/
    python -m pytest -v tests/test_health.py

2. 特定のテストメソッドだけ実行:
    python -m pytest -v tests/test_health.py::test_root_endpoint
    python -m pytest -v tests/test_health.py::test_root_endpoint_response_format
    python -m pytest -v tests/test_health.py::test_root_endpoint_http_method

3. カバレッジレポート生成:
    coverage run -m pytest tests/
    coverage report
    coverage html
"""

from fastapi.testclient import TestClient

from app.main import app


def test_root_endpoint(client: TestClient):
    """ルートのヘルスチェックエンドポイントのテスト

    ルートエンドポイント（/）が期待されるヘルスチェックメッセージを
    ステータスコード200で返すことを検証します。

    Args:
        client: conftest.pyから提供されるFastAPIテストクライアントフィクスチャ
    """
    # ルートエンドポイントにGETリクエストを送信
    response = client.get("/")

    # ステータスコードの検証
    assert response.status_code == 200

    # レスポンスボディの検証
    expected_response = {"message": "RAG Chat API is running"}
    assert response.json() == expected_response


def test_root_endpoint_response_format(client: TestClient):
    """ルートエンドポイントのレスポンス形式テスト

    ルートエンドポイントからのレスポンスが正しい構造と
    データ型を持っていることを検証します。

    Args:
        client: conftest.pyから提供されるFastAPIテストクライアントフィクスチャ
    """
    # ルートエンドポイントにGETリクエストを送信
    response = client.get("/")

    # ステータスコードの検証
    assert response.status_code == 200

    # JSONレスポンスの取得
    json_response = response.json()

    # レスポンス構造の検証
    assert "message" in json_response
    assert isinstance(json_response["message"], str)
    assert len(json_response["message"]) > 0


def test_root_endpoint_http_method():
    """ルートエンドポイントがGETリクエストのみを受け付けることのテスト

    ルートエンドポイントが異なるHTTPメソッドを適切に処理することを検証します。
    """
    # 独立したテストクライアントを作成
    client = TestClient(app)

    # GETは成功するはず
    response = client.get("/")
    assert response.status_code == 200

    # POSTは405 Method Not Allowedを返すはず
    response = client.post("/")
    assert response.status_code == 405

    # PUTは405 Method Not Allowedを返すはず
    response = client.put("/")
    assert response.status_code == 405
