"""
グループ関連エンドポイントのテストモジュール

テスト実行方法:
1. コマンドラインからの実行:
    python -m pytest -v tests/
    python -m pytest -v tests/test_groups.py

2. 特定のテストメソッドだけ実行:
    python -m pytest -v \
        tests/test_groups.py::TestCreateGroup::test_create_group_success
    python -m pytest -v tests/test_groups.py::TestGetGroup::test_get_group_success

3. カバレッジレポート生成:
    coverage run -m pytest tests/
    coverage report
    coverage html
"""

from unittest.mock import MagicMock
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.main import app
from app.config.database import get_db
from app.models.group import Group
from app.services.groups import GroupService


class TestCreateGroup:
    """グループ作成エンドポイントのテストクラス"""

    def test_create_group_success(self, client):
        """グループ作成の正常系テスト

        正常なグループデータを送信した際に、適切なレスポンスが返されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックグループオブジェクト
        mock_group = Group(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            id=1,
            name="testgroup",
            description="test description",
        )

        # GroupServiceのメソッドをモック化
        GroupService.is_name_taken = MagicMock(return_value=False)
        GroupService.create_group = MagicMock(return_value=mock_group)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        # データベースセッションをオーバーライド
        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ
            request_data = {
                "name": "testgroup",
                "description": "test description",
            }

            # APIリクエストを送信
            response = client.post("/api/groups/", json=request_data)

            # レスポンスの検証
            assert response.status_code == 201
            response_data = response.json()
            assert response_data["id"] == 1
            assert response_data["name"] == "testgroup"
            assert response_data["description"] == "test description"

            # サービスメソッドの呼び出し確認
            GroupService.is_name_taken.assert_called_once_with(mock_db, "testgroup")
            GroupService.create_group.assert_called_once()

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            GroupService.is_name_taken.reset_mock()
            GroupService.create_group.reset_mock()

    def test_create_group_without_description(self, client):
        """グループ作成の正常系テスト（説明なし）

        説明なしでグループを作成した際に、適切なレスポンスが返されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックグループオブジェクト（説明なし）
        mock_group = Group(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            id=1,
            name="testgroup",
            description=None,
        )

        # GroupServiceのメソッドをモック化
        GroupService.is_name_taken = MagicMock(return_value=False)
        GroupService.create_group = MagicMock(return_value=mock_group)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ（説明なし）
            request_data = {"name": "testgroup"}

            # APIリクエストを送信
            response = client.post("/api/groups/", json=request_data)

            # レスポンスの検証
            assert response.status_code == 201
            response_data = response.json()
            assert response_data["id"] == 1
            assert response_data["name"] == "testgroup"
            assert response_data["description"] is None

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            GroupService.is_name_taken.reset_mock()
            GroupService.create_group.reset_mock()

    def test_create_group_duplicate_name(self, client):
        """グループ作成の異常系テスト（重複するグループ名）

        既に存在するグループ名を使用した場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # GroupServiceのメソッドをモック化（名前重複）
        GroupService.is_name_taken = MagicMock(return_value=True)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ
            request_data = {
                "name": "existinggroup",
                "description": "test description",
            }

            # APIリクエストを送信
            response = client.post("/api/groups/", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 400
            response_data = response.json()
            assert "existinggroup" in response_data["detail"]
            assert "既に使用されています" in response_data["detail"]

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            GroupService.is_name_taken.reset_mock()

    def test_create_group_invalid_data(self, client):
        """グループ作成の異常系テスト（不正なデータ）

        バリデーションエラーが発生するデータを送信した場合のエラーハンドリングを検証します。
        """
        # 不正なリクエストデータ（nameフィールドが不足）
        invalid_request_data = {"description": "test description"}

        # APIリクエストを送信
        response = client.post("/api/groups/", json=invalid_request_data)

        # バリデーションエラーの検証
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data

        # nameフィールドが不足している旨のエラーを確認
        errors = response_data["detail"]
        assert any(error["loc"] == ["body", "name"] for error in errors)

    def test_create_group_empty_name(self, client):
        """グループ作成の異常系テスト（空のグループ名）

        グループ名が空の場合のバリデーションエラーを検証します。
        """
        # 空のグループ名のテストデータ
        request_data = {
            "name": "",
            "description": "test description",
        }

        # APIリクエストを送信
        response = client.post("/api/groups/", json=request_data)

        # バリデーションエラーの検証
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data

        # グループ名の長さに関するエラーを確認
        errors = response_data["detail"]
        assert any(error["loc"] == ["body", "name"] for error in errors)

    def test_create_group_integrity_error(self, client):
        """グループ作成の異常系テスト（データベース制約エラー）

        データベースレベルでの制約違反が発生した場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # GroupServiceのメソッドをモック化
        GroupService.is_name_taken = MagicMock(return_value=False)
        GroupService.create_group = MagicMock(side_effect=IntegrityError("", "", ""))

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ
            request_data = {
                "name": "testgroup",
                "description": "test description",
            }

            # APIリクエストを送信
            response = client.post("/api/groups/", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 400
            response_data = response.json()
            assert "既に使用されています" in response_data["detail"]

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            GroupService.is_name_taken.reset_mock()
            GroupService.create_group.reset_mock()


class TestGetGroup:
    """グループ取得エンドポイントのテストクラス"""

    def test_get_group_success(self, client):
        """グループ取得の正常系テスト

        存在するグループIDを指定した際に、適切なレスポンスが返されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックグループオブジェクト
        mock_group = Group(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            id=1,
            name="testgroup",
            description="test description",
        )

        # GroupServiceのメソッドをモック化
        GroupService.get_group_by_id = MagicMock(return_value=mock_group)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # APIリクエストを送信
            response = client.get("/api/groups/1")

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["id"] == 1
            assert response_data["name"] == "testgroup"
            assert response_data["description"] == "test description"

            # サービスメソッドの呼び出し確認
            GroupService.get_group_by_id.assert_called_once_with(mock_db, 1)

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            GroupService.get_group_by_id.reset_mock()

    def test_get_group_not_found(self, client):
        """グループ取得の異常系テスト（存在しないグループ）

        存在しないグループIDを指定した場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # GroupServiceのメソッドをモック化（グループが存在しない）
        GroupService.get_group_by_id = MagicMock(return_value=None)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # APIリクエストを送信
            response = client.get("/api/groups/999")

            # エラーレスポンスの検証
            assert response.status_code == 404
            response_data = response.json()
            assert "999" in response_data["detail"]
            assert "見つかりません" in response_data["detail"]

            # サービスメソッドの呼び出し確認
            GroupService.get_group_by_id.assert_called_once_with(mock_db, 999)

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            GroupService.get_group_by_id.reset_mock()

    def test_get_group_invalid_id(self, client):
        """グループ取得の異常系テスト（不正なグループID）

        数値以外のグループIDを指定した場合のエラーハンドリングを検証します。
        """
        # APIリクエストを送信（不正なID）
        response = client.get("/api/groups/invalid")

        # バリデーションエラーの検証
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data

        # パスパラメータのバリデーションエラーを確認
        errors = response_data["detail"]
        assert any(error["loc"] == ["path", "group_id"] for error in errors)


class TestGetAllGroups:
    """全グループ取得エンドポイントのテストクラス"""

    def test_get_all_groups_success(self, client):
        """全グループ取得の正常系テスト

        複数のグループが存在する場合に、適切なレスポンスが返されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックグループオブジェクトのリスト
        mock_groups = [
            Group(
                created_at=datetime.now(),
                updated_at=datetime.now(),
                id=1,
                name="group1",
                description="group1 description",
            ),
            Group(
                created_at=datetime.now(),
                updated_at=datetime.now(),
                id=2,
                name="group2",
                description="group2 description",
            ),
            Group(
                created_at=datetime.now(),
                updated_at=datetime.now(),
                id=3,
                name="group3",
                description=None,
            ),
        ]

        # GroupServiceのメソッドをモック化
        GroupService.get_all_groups = MagicMock(return_value=mock_groups)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # APIリクエストを送信
            response = client.get("/api/groups/")

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()

            # レスポンス構造の検証
            assert "groups" in response_data
            assert "total" in response_data
            assert response_data["total"] == 3

            # グループリストの検証
            groups = response_data["groups"]
            assert len(groups) == 3

            # 各グループのデータ検証
            assert groups[0]["id"] == 1
            assert groups[0]["name"] == "group1"
            assert groups[0]["description"] == "group1 description"

            assert groups[1]["id"] == 2
            assert groups[1]["name"] == "group2"
            assert groups[1]["description"] == "group2 description"

            assert groups[2]["id"] == 3
            assert groups[2]["name"] == "group3"
            assert groups[2]["description"] is None

            # サービスメソッドの呼び出し確認
            GroupService.get_all_groups.assert_called_once_with(mock_db)

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            GroupService.get_all_groups.reset_mock()

    def test_get_all_groups_empty(self, client):
        """全グループ取得の正常系テスト（グループが存在しない場合）

        グループが存在しない場合に、空のリストと0の総数が返されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # GroupServiceのメソッドをモック化（空のリストを返す）
        GroupService.get_all_groups = MagicMock(return_value=[])

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # APIリクエストを送信
            response = client.get("/api/groups/")

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()

            # レスポンス構造の検証
            assert "groups" in response_data
            assert "total" in response_data
            assert response_data["total"] == 0
            assert response_data["groups"] == []

            # サービスメソッドの呼び出し確認
            GroupService.get_all_groups.assert_called_once_with(mock_db)

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            GroupService.get_all_groups.reset_mock()

    def test_get_all_groups_single_group(self, client):
        """全グループ取得の正常系テスト（グループが1つの場合）

        グループが1つだけ存在する場合のレスポンスを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックグループオブジェクト（1つだけ）
        mock_group = Group(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            id=1,
            name="singlegroup",
            description="single group description",
        )

        # GroupServiceのメソッドをモック化
        GroupService.get_all_groups = MagicMock(return_value=[mock_group])

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # APIリクエストを送信
            response = client.get("/api/groups/")

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()

            # レスポンス構造の検証
            assert "groups" in response_data
            assert "total" in response_data
            assert response_data["total"] == 1

            # グループリストの検証
            groups = response_data["groups"]
            assert len(groups) == 1

            # グループデータの検証
            group = groups[0]
            assert group["id"] == 1
            assert group["name"] == "singlegroup"
            assert group["description"] == "single group description"

            # サービスメソッドの呼び出し確認
            GroupService.get_all_groups.assert_called_once_with(mock_db)

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            GroupService.get_all_groups.reset_mock()


class TestUpdateGroup:
    """グループ更新エンドポイントのテストクラス"""

    def test_update_group_name_only(self, client):
        """グループ更新の正常系テスト（名前のみ更新）

        名前のみを更新した際に、適切なレスポンスが返されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # 更新後のモックグループオブジェクト
        updated_group = Group(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            id=1,
            name="updatedgroup",
            description="original description",
        )

        # GroupServiceのメソッドをモック化
        GroupService.update_group = MagicMock(return_value=updated_group)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ（名前のみ更新）
            request_data = {"name": "updatedgroup"}

            # APIリクエストを送信
            response = client.put("/api/groups/1", json=request_data)

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["id"] == 1
            assert response_data["name"] == "updatedgroup"
            assert response_data["description"] == "original description"

            # サービスメソッドの呼び出し確認
            GroupService.update_group.assert_called_once()
            call_args = GroupService.update_group.call_args
            assert call_args[0][0] == mock_db  # データベースセッション
            assert call_args[0][1] == 1  # グループID

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            GroupService.update_group.reset_mock()

    def test_update_group_description_only(self, client):
        """グループ更新の正常系テスト（説明のみ更新）

        説明のみを更新した際に、適切なレスポンスが返されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # 更新後のモックグループオブジェクト
        updated_group = Group(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            id=1,
            name="originalgroup",
            description="updated description",
        )

        # GroupServiceのメソッドをモック化
        GroupService.update_group = MagicMock(return_value=updated_group)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ（説明のみ更新）
            request_data = {"description": "updated description"}

            # APIリクエストを送信
            response = client.put("/api/groups/1", json=request_data)

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["id"] == 1
            assert response_data["name"] == "originalgroup"
            assert response_data["description"] == "updated description"

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            GroupService.update_group.reset_mock()

    def test_update_group_all_fields(self, client):
        """グループ更新の正常系テスト（全フィールド更新）

        名前と説明を両方更新した際に、適切なレスポンスが返されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # 更新後のモックグループオブジェクト
        updated_group = Group(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            id=1,
            name="newgroup",
            description="new description",
        )

        # GroupServiceのメソッドをモック化
        GroupService.update_group = MagicMock(return_value=updated_group)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ（全フィールド更新）
            request_data = {
                "name": "newgroup",
                "description": "new description",
            }

            # APIリクエストを送信
            response = client.put("/api/groups/1", json=request_data)

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["id"] == 1
            assert response_data["name"] == "newgroup"
            assert response_data["description"] == "new description"

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            GroupService.update_group.reset_mock()

    def test_update_group_not_found(self, client):
        """グループ更新の異常系テスト（存在しないグループ）

        存在しないグループIDを指定した場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # GroupServiceのメソッドをモック化（グループが存在しない）
        GroupService.update_group = MagicMock(return_value=None)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ
            request_data = {"name": "newgroup"}

            # APIリクエストを送信
            response = client.put("/api/groups/999", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 404
            response_data = response.json()
            assert "999" in response_data["detail"]
            assert "見つかりません" in response_data["detail"]

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            GroupService.update_group.reset_mock()

    def test_update_group_duplicate_name(self, client):
        """グループ更新の異常系テスト（重複するグループ名）

        既に存在するグループ名に更新しようとした場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # GroupServiceのメソッドをモック化（IntegrityErrorを発生）
        GroupService.update_group = MagicMock(
            side_effect=IntegrityError("グループ名が既に使用されています", None, None)
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ（重複するグループ名）
            request_data = {"name": "existinggroup"}

            # APIリクエストを送信
            response = client.put("/api/groups/1", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 400
            response_data = response.json()
            assert "既に使用されています" in response_data["detail"]

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            GroupService.update_group.reset_mock()


class TestDeleteGroup:
    """グループ削除エンドポイントのテストクラス"""

    def test_delete_group_success(self, client):
        """グループ削除の正常系テスト"""
        mock_db = MagicMock()
        GroupService.delete_group_by_id = MagicMock(return_value=True)

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            response = client.delete("/api/groups/1")
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["message"] == "グループが正常に削除されました"
            assert response_data["deleted_count"] == 1
            GroupService.delete_group_by_id.assert_called_once_with(mock_db, 1)
        finally:
            app.dependency_overrides.clear()
            GroupService.delete_group_by_id.reset_mock()

    def test_delete_group_not_found(self, client):
        """グループ削除の異常系テスト（存在しないグループ）"""
        mock_db = MagicMock()
        GroupService.delete_group_by_id = MagicMock(return_value=False)

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            response = client.delete("/api/groups/999")
            assert response.status_code == 404
            response_data = response.json()
            assert "999" in response_data["detail"]
            assert "見つかりません" in response_data["detail"]
            GroupService.delete_group_by_id.assert_called_with(mock_db, 999)
        finally:
            app.dependency_overrides.clear()
            GroupService.delete_group_by_id.reset_mock()

    def test_delete_group_invalid_id(self, client):
        """グループ削除の異常系テスト（不正なグループID）"""
        response = client.delete("/api/groups/invalid")
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data
        errors = response_data["detail"]
        assert any(error["loc"] == ["path", "group_id"] for error in errors)

    def test_delete_group_database_error(self, client):
        """グループ削除の異常系テスト（データベースエラー）"""
        mock_db = MagicMock()
        GroupService.delete_group_by_id = MagicMock(
            side_effect=Exception("データベースエラー")
        )

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            response = client.delete("/api/groups/1")
            assert response.status_code == 500
            response_data = response.json()
            assert "エラーが発生しました" in response_data["detail"]
            assert "データベースエラー" in response_data["detail"]
            GroupService.delete_group_by_id.assert_called_once_with(mock_db, 1)
        finally:
            app.dependency_overrides.clear()
            GroupService.delete_group_by_id.reset_mock()


class TestDeleteAllGroups:
    """全グループ削除エンドポイントのテストクラス"""

    def test_delete_all_groups_success(self, client):
        """全グループ削除の正常系テスト"""
        mock_db = MagicMock()
        GroupService.delete_all_groups = MagicMock(return_value=3)

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            response = client.delete("/api/groups/")
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["message"] == "3個のグループが正常に削除されました"
            assert response_data["deleted_count"] == 3
            GroupService.delete_all_groups.assert_called_once_with(mock_db)
        finally:
            app.dependency_overrides.clear()
            GroupService.delete_all_groups.reset_mock()

    def test_delete_all_groups_empty(self, client):
        """全グループ削除の正常系テスト（グループが存在しない場合）"""
        mock_db = MagicMock()
        GroupService.delete_all_groups = MagicMock(return_value=0)

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            response = client.delete("/api/groups/")
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["message"] == "0個のグループが正常に削除されました"
            assert response_data["deleted_count"] == 0
            GroupService.delete_all_groups.assert_called_once_with(mock_db)
        finally:
            app.dependency_overrides.clear()
            GroupService.delete_all_groups.reset_mock()

    def test_delete_all_groups_database_error(self, client):
        """全グループ削除の異常系テスト（データベースエラー）"""
        mock_db = MagicMock()
        GroupService.delete_all_groups = MagicMock(
            side_effect=Exception("データベースエラー")
        )

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            response = client.delete("/api/groups/")
            assert response.status_code == 500
            response_data = response.json()
            assert "エラーが発生しました" in response_data["detail"]
            assert "データベースエラー" in response_data["detail"]
            GroupService.delete_all_groups.assert_called_once_with(mock_db)
        finally:
            app.dependency_overrides.clear()
            GroupService.delete_all_groups.reset_mock()


class TestGroupsIntegration:
    """グループエンドポイントの統合テストクラス"""

    def test_group_lifecycle(self, client):
        """グループのライフサイクルテスト

        グループの作成から取得までの一連の流れを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # 作成用のモックグループオブジェクト
        mock_created_group = Group(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            id=1,
            name="lifecyclegroup",
            description="lifecycle test group",
        )

        # GroupServiceのメソッドをモック化
        GroupService.is_name_taken = MagicMock(return_value=False)
        GroupService.create_group = MagicMock(return_value=mock_created_group)
        GroupService.get_group_by_id = MagicMock(return_value=mock_created_group)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # 1. グループ作成
            create_data = {
                "name": "lifecyclegroup",
                "description": "lifecycle test group",
            }

            create_response = client.post("/api/groups/", json=create_data)
            assert create_response.status_code == 201
            created_group = create_response.json()

            # 2. 作成されたグループを取得
            get_response = client.get(f"/api/groups/{created_group['id']}")
            assert get_response.status_code == 200
            retrieved_group = get_response.json()

            # 3. 作成されたグループと取得されたグループが同じであることを確認
            assert created_group["id"] == retrieved_group["id"]
            assert created_group["name"] == retrieved_group["name"]
            assert created_group["description"] == retrieved_group["description"]

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            GroupService.is_name_taken.reset_mock()
            GroupService.create_group.reset_mock()
            GroupService.get_group_by_id.reset_mock()

    def test_group_delete_lifecycle(self, client):
        """グループ削除のライフサイクルテスト"""
        mock_db = MagicMock()
        mock_created_group = Group(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            id=1,
            name="deletegroup",
            description="delete test group",
        )

        GroupService.is_name_taken = MagicMock(return_value=False)
        GroupService.create_group = MagicMock(return_value=mock_created_group)
        GroupService.delete_group_by_id = MagicMock(return_value=True)

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # 1. グループ作成
            create_data = {
                "name": "deletegroup",
                "description": "delete test group",
            }
            create_response = client.post("/api/groups/", json=create_data)
            assert create_response.status_code == 201
            created_group = create_response.json()

            # 2. 作成されたグループを削除
            delete_response = client.delete(f"/api/groups/{created_group['id']}")
            assert delete_response.status_code == 200
            delete_result = delete_response.json()

            # 3. 削除結果の検証
            assert delete_result["message"] == "グループが正常に削除されました"
            assert delete_result["deleted_count"] == 1
        finally:
            app.dependency_overrides.clear()
            GroupService.is_name_taken.reset_mock()
            GroupService.create_group.reset_mock()
            GroupService.delete_group_by_id.reset_mock()
