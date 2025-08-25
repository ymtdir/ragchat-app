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
from app.schemas.users import UserUpdate, UserDeleteResponse


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
                id=1,
                name="user1",
                email="user1@example.com",
                password="hashed_password1",
            ),
            User(
                id=2,
                name="user2",
                email="user2@example.com",
                password="hashed_password2",
            ),
            User(
                id=3,
                name="user3",
                email="user3@example.com",
                password="hashed_password3",
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


class TestUpdateUser:
    """ユーザー更新エンドポイントのテストクラス"""

    def test_update_user_name_only(self, client: TestClient):
        """ユーザー更新の正常系テスト（名前のみ更新）

        名前のみを更新した際に、適切なレスポンスが返されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # 更新後のモックユーザーオブジェクト
        updated_user = User(
            id=1,
            name="updateduser",
            email="original@example.com",
            password="hashed_password",
        )

        # UserServiceのメソッドをモック化
        UserService.update_user = MagicMock(return_value=updated_user)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ（名前のみ更新）
            request_data = {"name": "updateduser"}

            # APIリクエストを送信
            response = client.put("/api/users/1", json=request_data)

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["id"] == 1
            assert response_data["name"] == "updateduser"
            assert response_data["email"] == "original@example.com"
            assert "password" not in response_data

            # サービスメソッドの呼び出し確認
            # FastAPIによりリクエストボディがUserUpdateスキーマに変換されるため、
            # 実際の呼び出し引数を確認する
            UserService.update_user.assert_called_once()
            call_args = UserService.update_user.call_args
            assert call_args[0][0] == mock_db  # データベースセッション
            assert call_args[0][1] == 1  # ユーザーID
            # UserUpdateオブジェクトの内容を確認
            user_update = call_args[0][2]
            assert user_update.name == request_data.get("name")
            assert user_update.email == request_data.get("email")
            assert user_update.current_password == request_data.get("current_password")
            assert user_update.new_password == request_data.get("new_password")

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.update_user.reset_mock()

    def test_update_user_email_only(self, client: TestClient):
        """ユーザー更新の正常系テスト（メールアドレスのみ更新）

        メールアドレスのみを更新した際に、適切なレスポンスが返されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # 更新後のモックユーザーオブジェクト
        updated_user = User(
            id=1,
            name="originaluser",
            email="updated@example.com",
            password="hashed_password",
        )

        # UserServiceのメソッドをモック化
        UserService.update_user = MagicMock(return_value=updated_user)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ（メールアドレスのみ更新）
            request_data = {"email": "updated@example.com"}

            # APIリクエストを送信
            response = client.put("/api/users/1", json=request_data)

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["id"] == 1
            assert response_data["name"] == "originaluser"
            assert response_data["email"] == "updated@example.com"
            assert "password" not in response_data

            # サービスメソッドの呼び出し確認
            # FastAPIによりリクエストボディがUserUpdateスキーマに変換されるため、
            # 実際の呼び出し引数を確認する
            UserService.update_user.assert_called_once()
            call_args = UserService.update_user.call_args
            assert call_args[0][0] == mock_db  # データベースセッション
            assert call_args[0][1] == 1  # ユーザーID
            # UserUpdateオブジェクトの内容を確認
            user_update = call_args[0][2]
            assert user_update.name == request_data.get("name")
            assert user_update.email == request_data.get("email")
            assert user_update.current_password == request_data.get("current_password")
            assert user_update.new_password == request_data.get("new_password")

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.update_user.reset_mock()

    def test_update_user_password_only(self, client: TestClient):
        """ユーザー更新の正常系テスト（パスワードのみ更新）

        パスワードのみを更新した際に、適切なレスポンスが返されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # 更新後のモックユーザーオブジェクト
        updated_user = User(
            id=1,
            name="originaluser",
            email="original@example.com",
            password="new_hashed_password",
        )

        # UserServiceのメソッドをモック化
        UserService.update_user = MagicMock(return_value=updated_user)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ（パスワードのみ更新）
            request_data = {
                "current_password": "oldpassword",
                "new_password": "newpassword123",
            }

            # APIリクエストを送信
            response = client.put("/api/users/1", json=request_data)

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["id"] == 1
            assert response_data["name"] == "originaluser"
            assert response_data["email"] == "original@example.com"
            assert "password" not in response_data

            # サービスメソッドの呼び出し確認
            # FastAPIによりリクエストボディがUserUpdateスキーマに変換されるため、
            # 実際の呼び出し引数を確認する
            UserService.update_user.assert_called_once()
            call_args = UserService.update_user.call_args
            assert call_args[0][0] == mock_db  # データベースセッション
            assert call_args[0][1] == 1  # ユーザーID
            # UserUpdateオブジェクトの内容を確認
            user_update = call_args[0][2]
            assert user_update.name == request_data.get("name")
            assert user_update.email == request_data.get("email")
            assert user_update.current_password == request_data.get("current_password")
            assert user_update.new_password == request_data.get("new_password")

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.update_user.reset_mock()

    def test_update_user_all_fields(self, client: TestClient):
        """ユーザー更新の正常系テスト（全フィールド更新）

        名前、メールアドレス、パスワードを全て更新した際に、適切なレスポンスが返されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # 更新後のモックユーザーオブジェクト
        updated_user = User(
            id=1,
            name="newuser",
            email="new@example.com",
            password="new_hashed_password",
        )

        # UserServiceのメソッドをモック化
        UserService.update_user = MagicMock(return_value=updated_user)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ（全フィールド更新）
            request_data = {
                "name": "newuser",
                "email": "new@example.com",
                "current_password": "oldpassword",
                "new_password": "newpassword123",
            }

            # APIリクエストを送信
            response = client.put("/api/users/1", json=request_data)

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["id"] == 1
            assert response_data["name"] == "newuser"
            assert response_data["email"] == "new@example.com"
            assert "password" not in response_data

            # サービスメソッドの呼び出し確認
            # FastAPIによりリクエストボディがUserUpdateスキーマに変換されるため、
            # 実際の呼び出し引数を確認する
            UserService.update_user.assert_called_once()
            call_args = UserService.update_user.call_args
            assert call_args[0][0] == mock_db  # データベースセッション
            assert call_args[0][1] == 1  # ユーザーID
            # UserUpdateオブジェクトの内容を確認
            user_update = call_args[0][2]
            assert user_update.name == request_data.get("name")
            assert user_update.email == request_data.get("email")
            assert user_update.current_password == request_data.get("current_password")
            assert user_update.new_password == request_data.get("new_password")

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.update_user.reset_mock()

    def test_update_user_not_found(self, client: TestClient):
        """ユーザー更新の異常系テスト（存在しないユーザー）

        存在しないユーザーIDを指定した場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化（ユーザーが存在しない）
        UserService.update_user = MagicMock(return_value=None)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ
            request_data = {"name": "newuser"}

            # APIリクエストを送信
            response = client.put("/api/users/999", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 404
            response_data = response.json()
            assert "999" in response_data["detail"]
            assert "見つかりません" in response_data["detail"]

            # サービスメソッドの呼び出し確認
            # FastAPIによりリクエストボディがUserUpdateスキーマに変換されるため、
            # 実際の呼び出し引数を確認する
            UserService.update_user.assert_called_once()
            call_args = UserService.update_user.call_args
            assert call_args[0][0] == mock_db  # データベースセッション
            assert call_args[0][1] == 999  # ユーザーID
            # UserUpdateオブジェクトの内容を確認
            user_update = call_args[0][2]
            assert user_update.name == request_data.get("name")
            assert user_update.email == request_data.get("email")
            assert user_update.current_password == request_data.get("current_password")
            assert user_update.new_password == request_data.get("new_password")

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.update_user.reset_mock()

    def test_update_user_password_without_current(self, client: TestClient):
        """ユーザー更新の異常系テスト（パスワード変更時に現在のパスワードなし）

        新しいパスワードを指定したが現在のパスワードを指定しなかった場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化（ValueErrorを発生）
        UserService.update_user = MagicMock(
            side_effect=ValueError("パスワード変更には現在のパスワードが必要です")
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ（現在のパスワードなし）
            request_data = {"new_password": "newpassword123"}

            # APIリクエストを送信
            response = client.put("/api/users/1", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 400
            response_data = response.json()
            assert "現在のパスワードが必要です" in response_data["detail"]

            # サービスメソッドの呼び出し確認
            # FastAPIによりリクエストボディがUserUpdateスキーマに変換されるため、
            # 実際の呼び出し引数を確認する
            UserService.update_user.assert_called_once()
            call_args = UserService.update_user.call_args
            assert call_args[0][0] == mock_db  # データベースセッション
            assert call_args[0][1] == 1  # ユーザーID
            # UserUpdateオブジェクトの内容を確認
            user_update = call_args[0][2]
            assert user_update.name == request_data.get("name")
            assert user_update.email == request_data.get("email")
            assert user_update.current_password == request_data.get("current_password")
            assert user_update.new_password == request_data.get("new_password")

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.update_user.reset_mock()

    def test_update_user_wrong_current_password(self, client: TestClient):
        """ユーザー更新の異常系テスト（間違った現在のパスワード）

        現在のパスワードが間違っている場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化（ValueErrorを発生）
        UserService.update_user = MagicMock(
            side_effect=ValueError("現在のパスワードが正しくありません")
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ（間違った現在のパスワード）
            request_data = {
                "current_password": "wrongpassword",
                "new_password": "newpassword123",
            }

            # APIリクエストを送信
            response = client.put("/api/users/1", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 400
            response_data = response.json()
            assert "現在のパスワードが正しくありません" in response_data["detail"]

            # サービスメソッドの呼び出し確認
            # FastAPIによりリクエストボディがUserUpdateスキーマに変換されるため、
            # 実際の呼び出し引数を確認する
            UserService.update_user.assert_called_once()
            call_args = UserService.update_user.call_args
            assert call_args[0][0] == mock_db  # データベースセッション
            assert call_args[0][1] == 1  # ユーザーID
            # UserUpdateオブジェクトの内容を確認
            user_update = call_args[0][2]
            assert user_update.name == request_data.get("name")
            assert user_update.email == request_data.get("email")
            assert user_update.current_password == request_data.get("current_password")
            assert user_update.new_password == request_data.get("new_password")

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.update_user.reset_mock()

    def test_update_user_duplicate_name(self, client: TestClient):
        """ユーザー更新の異常系テスト（重複するユーザー名）

        既に存在するユーザー名に更新しようとした場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化（IntegrityErrorを発生）
        UserService.update_user = MagicMock(
            side_effect=IntegrityError("ユーザー名が既に使用されています", None, None)
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ（重複するユーザー名）
            request_data = {"name": "existinguser"}

            # APIリクエストを送信
            response = client.put("/api/users/1", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 400
            response_data = response.json()
            assert "既に使用されています" in response_data["detail"]

            # サービスメソッドの呼び出し確認
            # FastAPIによりリクエストボディがUserUpdateスキーマに変換されるため、
            # 実際の呼び出し引数を確認する
            UserService.update_user.assert_called_once()
            call_args = UserService.update_user.call_args
            assert call_args[0][0] == mock_db  # データベースセッション
            assert call_args[0][1] == 1  # ユーザーID
            # UserUpdateオブジェクトの内容を確認
            user_update = call_args[0][2]
            assert user_update.name == request_data.get("name")
            assert user_update.email == request_data.get("email")
            assert user_update.current_password == request_data.get("current_password")
            assert user_update.new_password == request_data.get("new_password")

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.update_user.reset_mock()

    def test_update_user_duplicate_email(self, client: TestClient):
        """ユーザー更新の異常系テスト（重複するメールアドレス）

        既に存在するメールアドレスに更新しようとした場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化（IntegrityErrorを発生）
        UserService.update_user = MagicMock(
            side_effect=IntegrityError(
                "メールアドレスが既に使用されています", None, None
            )
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ（重複するメールアドレス）
            request_data = {"email": "existing@example.com"}

            # APIリクエストを送信
            response = client.put("/api/users/1", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 400
            response_data = response.json()
            assert "既に使用されています" in response_data["detail"]

            # サービスメソッドの呼び出し確認
            # FastAPIによりリクエストボディがUserUpdateスキーマに変換されるため、
            # 実際の呼び出し引数を確認する
            UserService.update_user.assert_called_once()
            call_args = UserService.update_user.call_args
            assert call_args[0][0] == mock_db  # データベースセッション
            assert call_args[0][1] == 1  # ユーザーID
            # UserUpdateオブジェクトの内容を確認
            user_update = call_args[0][2]
            assert user_update.name == request_data.get("name")
            assert user_update.email == request_data.get("email")
            assert user_update.current_password == request_data.get("current_password")
            assert user_update.new_password == request_data.get("new_password")

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.update_user.reset_mock()

    def test_update_user_invalid_data(self, client: TestClient):
        """ユーザー更新の異常系テスト（不正なデータ）

        バリデーションエラーが発生するデータを送信した場合のエラーハンドリングを検証します。
        """
        # 不正なリクエストデータ（短すぎる名前）
        invalid_request_data = {"name": "ab"}  # 3文字未満

        # APIリクエストを送信
        response = client.put("/api/users/1", json=invalid_request_data)

        # バリデーションエラーの検証
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data

        # 名前の長さに関するエラーを確認
        errors = response_data["detail"]
        assert any(error["loc"] == ["body", "name"] for error in errors)

    def test_update_user_short_new_password(self, client: TestClient):
        """ユーザー更新の異常系テスト（短すぎる新しいパスワード）

        新しいパスワードが8文字未満の場合のバリデーションエラーを検証します。
        """
        # 短いパスワードのテストデータ
        request_data = {
            "current_password": "oldpassword",
            "new_password": "123",  # 8文字未満
        }

        # APIリクエストを送信
        response = client.put("/api/users/1", json=request_data)

        # バリデーションエラーの検証
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data

        # パスワードの長さに関するエラーを確認
        errors = response_data["detail"]
        assert any(error["loc"] == ["body", "new_password"] for error in errors)

    def test_update_user_invalid_email(self, client: TestClient):
        """ユーザー更新の異常系テスト（不正なメールアドレス）

        不正な形式のメールアドレスを送信した場合のバリデーションエラーを検証します。
        """
        # 不正なメールアドレスのテストデータ
        request_data = {"email": "invalid-email"}  # 不正な形式

        # APIリクエストを送信
        response = client.put("/api/users/1", json=request_data)

        # バリデーションエラーの検証
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data

        # メールアドレスの形式に関するエラーを確認
        errors = response_data["detail"]
        assert any(error["loc"] == ["body", "email"] for error in errors)

    def test_update_user_invalid_id(self, client: TestClient):
        """ユーザー更新の異常系テスト（不正なユーザーID）

        数値以外のユーザーIDを指定した場合のエラーハンドリングを検証します。
        """
        # テストデータ
        request_data = {"name": "newuser"}

        # APIリクエストを送信（不正なID）
        response = client.put("/api/users/invalid", json=request_data)

        # バリデーションエラーの検証
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data

        # パスパラメータのバリデーションエラーを確認
        errors = response_data["detail"]
        assert any(error["loc"] == ["path", "user_id"] for error in errors)


class TestDeleteUser:
    """ユーザー削除エンドポイントのテストクラス"""

    def test_delete_user_success(self, client: TestClient):
        """ユーザー削除の正常系テスト"""
        mock_db = MagicMock()
        UserService.delete_user_by_id = MagicMock(return_value=True)

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            response = client.delete("/api/users/1")
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["message"] == "ユーザーが正常に削除されました"
            assert response_data["deleted_count"] == 1
            UserService.delete_user_by_id.assert_called_once_with(mock_db, 1)
        finally:
            app.dependency_overrides.clear()
            UserService.delete_user_by_id.reset_mock()

    def test_delete_user_not_found(self, client: TestClient):
        """ユーザー削除の異常系テスト（存在しないユーザー）"""
        mock_db = MagicMock()
        UserService.delete_user_by_id = MagicMock(return_value=False)

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            response = client.delete("/api/users/999")
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            assert response.status_code == 404
            response_data = response.json()
            assert "999" in response_data["detail"]
            assert "見つかりません" in response_data["detail"]
            # モックが正しく呼び出されたことを確認
            UserService.delete_user_by_id.assert_called_with(mock_db, 999)
        finally:
            app.dependency_overrides.clear()
            UserService.delete_user_by_id.reset_mock()

    def test_delete_user_invalid_id(self, client: TestClient):
        """ユーザー削除の異常系テスト（不正なユーザーID）"""
        response = client.delete("/api/users/invalid")
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data
        errors = response_data["detail"]
        assert any(error["loc"] == ["path", "user_id"] for error in errors)

    def test_delete_user_database_error(self, client: TestClient):
        """ユーザー削除の異常系テスト（データベースエラー）"""
        mock_db = MagicMock()
        UserService.delete_user_by_id = MagicMock(
            side_effect=Exception("データベースエラー")
        )

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            response = client.delete("/api/users/1")
            assert response.status_code == 500
            response_data = response.json()
            assert "エラーが発生しました" in response_data["detail"]
            assert "データベースエラー" in response_data["detail"]
            UserService.delete_user_by_id.assert_called_once_with(mock_db, 1)
        finally:
            app.dependency_overrides.clear()
            UserService.delete_user_by_id.reset_mock()


class TestDeleteAllUsers:
    """全ユーザー削除エンドポイントのテストクラス"""

    def test_delete_all_users_success(self, client: TestClient):
        """全ユーザー削除の正常系テスト"""
        mock_db = MagicMock()
        UserService.delete_all_users = MagicMock(return_value=3)

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            response = client.delete("/api/users/")
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["message"] == "3人のユーザーが正常に削除されました"
            assert response_data["deleted_count"] == 3
            UserService.delete_all_users.assert_called_once_with(mock_db)
        finally:
            app.dependency_overrides.clear()
            UserService.delete_all_users.reset_mock()

    def test_delete_all_users_empty(self, client: TestClient):
        """全ユーザー削除の正常系テスト（ユーザーが存在しない場合）"""
        mock_db = MagicMock()
        UserService.delete_all_users = MagicMock(return_value=0)

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            response = client.delete("/api/users/")
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["message"] == "0人のユーザーが正常に削除されました"
            assert response_data["deleted_count"] == 0
            UserService.delete_all_users.assert_called_once_with(mock_db)
        finally:
            app.dependency_overrides.clear()
            UserService.delete_all_users.reset_mock()

    def test_delete_all_users_single_user(self, client: TestClient):
        """全ユーザー削除の正常系テスト（ユーザーが1人の場合）"""
        mock_db = MagicMock()
        UserService.delete_all_users = MagicMock(return_value=1)

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            response = client.delete("/api/users/")
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["message"] == "1人のユーザーが正常に削除されました"
            assert response_data["deleted_count"] == 1
            UserService.delete_all_users.assert_called_once_with(mock_db)
        finally:
            app.dependency_overrides.clear()
            UserService.delete_all_users.reset_mock()

    def test_delete_all_users_database_error(self, client: TestClient):
        """全ユーザー削除の異常系テスト（データベースエラー）"""
        mock_db = MagicMock()
        UserService.delete_all_users = MagicMock(
            side_effect=Exception("データベースエラー")
        )

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            response = client.delete("/api/users/")
            assert response.status_code == 500
            response_data = response.json()
            assert "エラーが発生しました" in response_data["detail"]
            assert "データベースエラー" in response_data["detail"]
            UserService.delete_all_users.assert_called_once_with(mock_db)
        finally:
            app.dependency_overrides.clear()
            UserService.delete_all_users.reset_mock()


class TestUserDeleteIntegration:
    """ユーザー削除エンドポイントの統合テストクラス"""

    def test_user_delete_lifecycle(self, client: TestClient):
        """ユーザー削除のライフサイクルテスト"""
        mock_db = MagicMock()
        mock_created_user = User(
            id=1,
            name="deleteuser",
            email="delete@example.com",
            password="hashed_password",
        )

        UserService.is_name_taken = MagicMock(return_value=False)
        UserService.is_email_taken = MagicMock(return_value=False)
        UserService.create_user = MagicMock(return_value=mock_created_user)
        UserService.delete_user_by_id = MagicMock(return_value=True)

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # 1. ユーザー作成
            create_data = {
                "name": "deleteuser",
                "email": "delete@example.com",
                "password": "password123",
            }
            create_response = client.post("/api/users/", json=create_data)
            assert create_response.status_code == 201
            created_user = create_response.json()

            # 2. 作成されたユーザーを削除
            delete_response = client.delete(f"/api/users/{created_user['id']}")
            assert delete_response.status_code == 200
            delete_result = delete_response.json()

            # 3. 削除結果の検証
            assert delete_result["message"] == "ユーザーが正常に削除されました"
            assert delete_result["deleted_count"] == 1
        finally:
            app.dependency_overrides.clear()
            UserService.is_name_taken.reset_mock()
            UserService.is_email_taken.reset_mock()
            UserService.create_user.reset_mock()
            UserService.delete_user_by_id.reset_mock()
