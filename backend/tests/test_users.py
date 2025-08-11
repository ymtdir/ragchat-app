"""
ユーザー関連エンドポイントのテストモジュール

テスト実行方法:
1. コマンドラインからの実行:
    python -m pytest -v tests/
    python -m pytest -v tests/test_users.py

2. 特定のテストメソッドだけ実行:
    python -m pytest -v \
        tests/test_users.py::TestCreateUser::test_create_user_success
    python -m pytest -v tests/test_users.py::TestGetUser::test_get_user_success

3. カバレッジレポート生成:
    coverage run -m pytest tests/
    coverage report
    coverage html
"""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.main import app
from app.config.database import get_db
from app.models.user import User
from app.services.users import UserService


class TestCreateUser:
    """ユーザー作成エンドポイントのテストクラス"""

    def test_create_user_success(self, client: TestClient):
        """ユーザー作成の正常系テスト

        正常なユーザーデータを送信した際に、適切なレスポンスが返されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト
        mock_user = User(
            id=1, name="testuser", email="test@example.com", password="hashed_password"
        )

        # UserServiceのメソッドをモック化
        UserService.is_name_taken = MagicMock(return_value=False)
        UserService.is_email_taken = MagicMock(return_value=False)
        UserService.create_user = MagicMock(return_value=mock_user)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        # データベースセッションをオーバーライド
        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ
            request_data = {
                "name": "testuser",
                "email": "test@example.com",
                "password": "password123",
            }

            # APIリクエストを送信
            response = client.post("/api/users/", json=request_data)

            # レスポンスの検証
            assert response.status_code == 201
            response_data = response.json()
            assert response_data["id"] == 1
            assert response_data["name"] == "testuser"
            assert response_data["email"] == "test@example.com"
            assert "password" not in response_data  # パスワードは含まれない

            # サービスメソッドの呼び出し確認
            UserService.is_name_taken.assert_called_once_with(mock_db, "testuser")
            UserService.is_email_taken.assert_called_once_with(
                mock_db, "test@example.com"
            )
            UserService.create_user.assert_called_once()

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.is_name_taken.reset_mock()
            UserService.is_email_taken.reset_mock()
            UserService.create_user.reset_mock()

    def test_create_user_duplicate_name(self, client: TestClient):
        """ユーザー作成の異常系テスト（重複するユーザー名）

        既に存在するユーザー名を使用した場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化（ユーザー名重複）
        UserService.is_name_taken = MagicMock(return_value=True)
        UserService.is_email_taken = MagicMock(return_value=False)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ
            request_data = {
                "name": "existinguser",
                "email": "new@example.com",
                "password": "password123",
            }

            # APIリクエストを送信
            response = client.post("/api/users/", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 400
            response_data = response.json()
            assert "existinguser" in response_data["detail"]
            assert "既に使用されています" in response_data["detail"]

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.is_name_taken.reset_mock()
            UserService.is_email_taken.reset_mock()

    def test_create_user_duplicate_email(self, client: TestClient):
        """ユーザー作成の異常系テスト（重複するメールアドレス）

        既に存在するメールアドレスを使用した場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化（メール重複）
        UserService.is_name_taken = MagicMock(return_value=False)
        UserService.is_email_taken = MagicMock(return_value=True)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ
            request_data = {
                "name": "newuser",
                "email": "existing@example.com",
                "password": "password123",
            }

            # APIリクエストを送信
            response = client.post("/api/users/", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 400
            response_data = response.json()
            assert "existing@example.com" in response_data["detail"]
            assert "既に使用されています" in response_data["detail"]

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.is_name_taken.reset_mock()
            UserService.is_email_taken.reset_mock()

    def test_create_user_invalid_data(self, client: TestClient):
        """ユーザー作成の異常系テスト（不正なデータ）

        バリデーションエラーが発生するデータを送信した場合のエラーハンドリングを検証します。
        """
        # 不正なリクエストデータ（nameフィールドが不足）
        invalid_request_data = {"email": "test@example.com", "password": "password123"}

        # APIリクエストを送信
        response = client.post("/api/users/", json=invalid_request_data)

        # バリデーションエラーの検証
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data

        # nameフィールドが不足している旨のエラーを確認
        errors = response_data["detail"]
        assert any(error["loc"] == ["body", "name"] for error in errors)

    def test_create_user_short_password(self, client: TestClient):
        """ユーザー作成の異常系テスト（短すぎるパスワード）

        パスワードが8文字未満の場合のバリデーションエラーを検証します。
        """
        # 短いパスワードのテストデータ
        request_data = {
            "name": "testuser",
            "email": "test@example.com",
            "password": "123",  # 8文字未満
        }

        # APIリクエストを送信
        response = client.post("/api/users/", json=request_data)

        # バリデーションエラーの検証
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data

        # パスワードの長さに関するエラーを確認
        errors = response_data["detail"]
        assert any(error["loc"] == ["body", "password"] for error in errors)

    def test_create_user_integrity_error(self, client: TestClient):
        """ユーザー作成の異常系テスト（データベース制約エラー）

        データベースレベルでの制約違反が発生した場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化
        UserService.is_name_taken = MagicMock(return_value=False)
        UserService.is_email_taken = MagicMock(return_value=False)
        UserService.create_user = MagicMock(side_effect=IntegrityError("", "", ""))

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ
            request_data = {
                "name": "testuser",
                "email": "test@example.com",
                "password": "password123",
            }

            # APIリクエストを送信
            response = client.post("/api/users/", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 400
            response_data = response.json()
            assert "既に使用されています" in response_data["detail"]

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.is_name_taken.reset_mock()
            UserService.is_email_taken.reset_mock()
            UserService.create_user.reset_mock()


class TestGetUser:
    """ユーザー取得エンドポイントのテストクラス"""

    def test_get_user_success(self, client: TestClient):
        """ユーザー取得の正常系テスト

        存在するユーザーIDを指定した際に、適切なレスポンスが返されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト
        mock_user = User(
            id=1, name="testuser", email="test@example.com", password="hashed_password"
        )

        # UserServiceのメソッドをモック化
        UserService.get_user_by_id = MagicMock(return_value=mock_user)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # APIリクエストを送信
            response = client.get("/api/users/1")

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["id"] == 1
            assert response_data["name"] == "testuser"
            assert response_data["email"] == "test@example.com"
            assert "password" not in response_data  # パスワードは含まれない

            # サービスメソッドの呼び出し確認
            UserService.get_user_by_id.assert_called_once_with(mock_db, 1)

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.get_user_by_id.reset_mock()

    def test_get_user_not_found(self, client: TestClient):
        """ユーザー取得の異常系テスト（存在しないユーザー）

        存在しないユーザーIDを指定した場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化（ユーザーが存在しない）
        UserService.get_user_by_id = MagicMock(return_value=None)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # APIリクエストを送信
            response = client.get("/api/users/999")

            # エラーレスポンスの検証
            assert response.status_code == 404
            response_data = response.json()
            assert "999" in response_data["detail"]
            assert "見つかりません" in response_data["detail"]

            # サービスメソッドの呼び出し確認
            UserService.get_user_by_id.assert_called_once_with(mock_db, 999)

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.get_user_by_id.reset_mock()

    def test_get_user_invalid_id(self, client: TestClient):
        """ユーザー取得の異常系テスト（不正なユーザーID）

        数値以外のユーザーIDを指定した場合のエラーハンドリングを検証します。
        """
        # APIリクエストを送信（不正なID）
        response = client.get("/api/users/invalid")

        # バリデーションエラーの検証
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data

        # パスパラメータのバリデーションエラーを確認
        errors = response_data["detail"]
        assert any(error["loc"] == ["path", "user_id"] for error in errors)


class TestGetAllUsers:
    """全ユーザー取得エンドポイントのテストクラス"""

    def test_get_all_users_success(self, client: TestClient):
        """全ユーザー取得の正常系テスト

        複数のユーザーが存在する場合に、適切なレスポンスが返されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクトのリスト
        mock_users = [
            User(
                id=1, name="user1", email="user1@example.com",
                password="hashed_password1"
            ),
            User(
                id=2, name="user2", email="user2@example.com",
                password="hashed_password2"
            ),
            User(
                id=3, name="user3", email="user3@example.com",
                password="hashed_password3"
            ),
        ]

        # UserServiceのメソッドをモック化
        UserService.get_all_users = MagicMock(return_value=mock_users)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # APIリクエストを送信
            response = client.get("/api/users/")

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()

            # レスポンス構造の検証
            assert "users" in response_data
            assert "total" in response_data
            assert response_data["total"] == 3

            # ユーザーリストの検証
            users = response_data["users"]
            assert len(users) == 3

            # 各ユーザーのデータ検証
            for i, user in enumerate(users):
                assert user["id"] == i + 1
                assert user["name"] == f"user{i + 1}"
                assert user["email"] == f"user{i + 1}@example.com"
                assert "password" not in user  # パスワードは含まれない

            # サービスメソッドの呼び出し確認
            UserService.get_all_users.assert_called_once_with(mock_db)

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.get_all_users.reset_mock()

    def test_get_all_users_empty(self, client: TestClient):
        """全ユーザー取得の正常系テスト（ユーザーが存在しない場合）

        ユーザーが存在しない場合に、空のリストと0の総数が返されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化（空のリストを返す）
        UserService.get_all_users = MagicMock(return_value=[])

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # APIリクエストを送信
            response = client.get("/api/users/")

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()

            # レスポンス構造の検証
            assert "users" in response_data
            assert "total" in response_data
            assert response_data["total"] == 0
            assert response_data["users"] == []

            # サービスメソッドの呼び出し確認
            UserService.get_all_users.assert_called_once_with(mock_db)

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.get_all_users.reset_mock()

    def test_get_all_users_single_user(self, client: TestClient):
        """全ユーザー取得の正常系テスト（ユーザーが1人の場合）

        ユーザーが1人だけ存在する場合のレスポンスを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト（1人だけ）
        mock_user = User(
            id=1,
            name="singleuser",
            email="single@example.com",
            password="hashed_password",
        )

        # UserServiceのメソッドをモック化
        UserService.get_all_users = MagicMock(return_value=[mock_user])

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # APIリクエストを送信
            response = client.get("/api/users/")

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()

            # レスポンス構造の検証
            assert "users" in response_data
            assert "total" in response_data
            assert response_data["total"] == 1

            # ユーザーリストの検証
            users = response_data["users"]
            assert len(users) == 1

            # ユーザーデータの検証
            user = users[0]
            assert user["id"] == 1
            assert user["name"] == "singleuser"
            assert user["email"] == "single@example.com"
            assert "password" not in user  # パスワードは含まれない

            # サービスメソッドの呼び出し確認
            UserService.get_all_users.assert_called_once_with(mock_db)

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.get_all_users.reset_mock()


class TestUsersIntegration:
    """ユーザーエンドポイントの統合テストクラス"""

    def test_user_lifecycle(self, client: TestClient):
        """ユーザーのライフサイクルテスト

        ユーザーの作成から取得までの一連の流れを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # 作成用のモックユーザーオブジェクト
        mock_created_user = User(
            id=1,
            name="lifecycleuser",
            email="lifecycle@example.com",
            password="hashed_password",
        )

        # UserServiceのメソッドをモック化
        UserService.is_name_taken = MagicMock(return_value=False)
        UserService.is_email_taken = MagicMock(return_value=False)
        UserService.create_user = MagicMock(return_value=mock_created_user)
        UserService.get_user_by_id = MagicMock(return_value=mock_created_user)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # 1. ユーザー作成
            create_data = {
                "name": "lifecycleuser",
                "email": "lifecycle@example.com",
                "password": "password123",
            }

            create_response = client.post("/api/users/", json=create_data)
            assert create_response.status_code == 201
            created_user = create_response.json()

            # 2. 作成されたユーザーを取得
            get_response = client.get(f"/api/users/{created_user['id']}")
            assert get_response.status_code == 200
            retrieved_user = get_response.json()

            # 3. 作成されたユーザーと取得されたユーザーが同じであることを確認
            assert created_user["id"] == retrieved_user["id"]
            assert created_user["name"] == retrieved_user["name"]
            assert created_user["email"] == retrieved_user["email"]

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.is_name_taken.reset_mock()
            UserService.is_email_taken.reset_mock()
            UserService.create_user.reset_mock()
            UserService.get_user_by_id.reset_mock()
