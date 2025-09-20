"""
メンバーシップ関連エンドポイントのテストモジュール

テスト実行方法:
1. コマンドラインからの実行:
    python -m pytest -v tests/
    python -m pytest -v tests/test_memberships.py

2. 特定のテストメソッドだけ実行:
    python -m pytest -v \
        tests/test_memberships.py::TestMemberships::test_add_member_to_group_success
    python -m pytest -v \
        tests/test_memberships.py::TestMemberships::test_get_group_members

3. カバレッジレポート生成:
    coverage run -m pytest tests/
    coverage report
    coverage html
"""

from unittest.mock import MagicMock
from datetime import datetime
from fastapi.testclient import TestClient
from app.models.membership import Membership
from app.services.memberships import MembershipService
from app.main import app
from app.config.database import get_db


class TestMemberships:
    """メンバーシップAPIのテストクラス"""

    def setup_method(self):
        """各テストメソッド実行前の準備"""
        pass

    def test_add_member_to_group_success(self, client: TestClient):
        """グループメンバー追加 - 成功"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックメンバーシップオブジェクト
        mock_membership = Membership(
            id=1,
            user_id=1,
            group_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # MembershipServiceのメソッドをモック化
        MembershipService.add_member_to_group = MagicMock(return_value=mock_membership)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # メンバー追加
            response = client.post(
                "/api/memberships/", json={"user_id": 1, "group_id": 1}
            )

            assert response.status_code == 201
            data = response.json()
            assert data["user_id"] == 1
            assert data["group_id"] == 1
            assert "created_at" in data

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.add_member_to_group.assert_called_once_with(mock_db, 1, 1)
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_add_member_to_group_user_not_found(self, client: TestClient):
        """グループメンバー追加 - ユーザーが存在しない"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（エラーを発生させる）
        MembershipService.add_member_to_group = MagicMock(
            side_effect=ValueError("ID 999 のユーザーが見つかりません")
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # 存在しないユーザーでメンバー追加
            response = client.post(
                "/api/memberships/", json={"user_id": 999, "group_id": 1}
            )

            assert response.status_code == 400
            assert "ユーザーが見つかりません" in response.json()["detail"]

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.add_member_to_group.assert_called_once_with(
                mock_db, 1, 999
            )
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_add_member_to_group_group_not_found(self, client: TestClient):
        """グループメンバー追加 - グループが存在しない"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（エラーを発生させる）
        MembershipService.add_member_to_group = MagicMock(
            side_effect=ValueError("ID 999 のグループが見つかりません")
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # 存在しないグループでメンバー追加
            response = client.post(
                "/api/memberships/", json={"user_id": 1, "group_id": 999}
            )

            assert response.status_code == 400
            assert "グループが見つかりません" in response.json()["detail"]

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.add_member_to_group.assert_called_once_with(
                mock_db, 999, 1
            )
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_remove_member_from_group_success(self, client: TestClient):
        """グループメンバー削除 - 成功"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（成功を返す）
        MembershipService.remove_member_from_group = MagicMock(return_value=True)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # メンバー削除
            response = client.delete("/api/memberships/groups/1/users/1")

            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "メンバーが正常に削除されました"
            assert data["deleted_count"] == 1

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.remove_member_from_group.assert_called_once_with(
                mock_db, 1, 1
            )
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_remove_member_from_group_not_found(self, client: TestClient):
        """グループメンバー削除 - メンバーが見つからない"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（Falseを返す）
        MembershipService.remove_member_from_group = MagicMock(return_value=False)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # 存在しないメンバーを削除
            response = client.delete("/api/memberships/groups/1/users/999")

            assert response.status_code == 404
            assert (
                "指定されたメンバーシップが見つかりません" in response.json()["detail"]
            )

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.remove_member_from_group.assert_called_once_with(
                mock_db, 1, 999
            )
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_remove_member_from_group_value_error(self, client: TestClient):
        """グループメンバー削除 - ValueError"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（ValueErrorを発生させる）
        MembershipService.remove_member_from_group = MagicMock(
            side_effect=ValueError("ID 999 のメンバーが見つかりません")
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # 存在しないメンバーを削除
            response = client.delete("/api/memberships/groups/1/users/999")

            assert response.status_code == 404
            assert "メンバーが見つかりません" in response.json()["detail"]

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.remove_member_from_group.assert_called_once_with(
                mock_db, 1, 999
            )
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_get_group_members_success(self, client: TestClient):
        """グループメンバー一覧取得 - 成功"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックメンバーリスト
        mock_members = [
            {"id": 1, "username": "user1", "email": "user1@example.com"},
            {"id": 2, "username": "user2", "email": "user2@example.com"},
        ]

        # MembershipServiceのメソッドをモック化
        MembershipService.get_group_members = MagicMock(return_value=mock_members)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # グループメンバー一覧取得
            response = client.get("/api/memberships/groups/1/members")

            assert response.status_code == 200
            data = response.json()
            assert data["group_id"] == 1
            assert data["total_count"] == 2
            assert len(data["members"]) == 2
            assert data["members"][0]["username"] == "user1"

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.get_group_members.assert_called_once_with(
                mock_db, 1, False
            )
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_get_group_members_with_deleted(self, client: TestClient):
        """グループメンバー一覧取得 - 削除済み含む"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックメンバーリスト
        mock_members = [
            {"id": 1, "username": "user1", "email": "user1@example.com"},
        ]

        # MembershipServiceのメソッドをモック化
        MembershipService.get_group_members = MagicMock(return_value=mock_members)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # 削除済み含むグループメンバー一覧取得
            response = client.get(
                "/api/memberships/groups/1/members?include_deleted=true"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["group_id"] == 1
            assert data["total_count"] == 1

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.get_group_members.assert_called_once_with(
                mock_db, 1, True
            )
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_get_user_groups_success(self, client: TestClient):
        """ユーザー所属グループ一覧取得 - 成功"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックグループリスト
        mock_groups = [
            {"id": 1, "name": "group1", "description": "Group 1"},
            {"id": 2, "name": "group2", "description": "Group 2"},
        ]

        # MembershipServiceのメソッドをモック化
        MembershipService.get_user_groups = MagicMock(return_value=mock_groups)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # ユーザー所属グループ一覧取得
            response = client.get("/api/memberships/users/1/groups")

            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == 1
            assert data["total_count"] == 2
            assert len(data["groups"]) == 2
            assert data["groups"][0]["name"] == "group1"

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.get_user_groups.assert_called_once_with(mock_db, 1, False)
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_add_multiple_members_to_group_success(self, client: TestClient):
        """複数メンバー一括追加 - 成功"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # モック結果
        mock_result = {"added_count": 2, "already_member_count": 1, "errors": []}

        # MembershipServiceのメソッドをモック化
        MembershipService.add_multiple_members_to_group = MagicMock(
            return_value=mock_result
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # 複数メンバー一括追加
            response = client.post(
                "/api/memberships/bulk-add", json={"group_id": 1, "user_ids": [1, 2, 3]}
            )

            assert response.status_code == 201
            data = response.json()
            assert data["group_id"] == 1
            assert data["added_count"] == 2
            assert data["already_member_count"] == 1
            assert data["errors"] == []

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.add_multiple_members_to_group.assert_called_once_with(
                mock_db, 1, [1, 2, 3]
            )
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_add_multiple_members_to_group_value_error(self, client: TestClient):
        """複数メンバー一括追加 - ValueError"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（ValueErrorを発生させる）
        MembershipService.add_multiple_members_to_group = MagicMock(
            side_effect=ValueError("ID 999 のグループが見つかりません")
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # 存在しないグループに複数メンバー追加
            response = client.post(
                "/api/memberships/bulk-add", json={"group_id": 999, "user_ids": [1, 2]}
            )

            assert response.status_code == 400
            assert "グループが見つかりません" in response.json()["detail"]

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.add_multiple_members_to_group.assert_called_once_with(
                mock_db, 999, [1, 2]
            )
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_remove_multiple_members_from_group_success(self, client: TestClient):
        """複数メンバー一括削除 - 成功"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # モック結果
        mock_result = {"removed_count": 2, "not_member_count": 1, "errors": []}

        # MembershipServiceのメソッドをモック化
        MembershipService.remove_multiple_members_from_group = MagicMock(
            return_value=mock_result
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # 複数メンバー一括削除
            response = client.post(
                "/api/memberships/bulk-remove",
                json={"group_id": 1, "user_ids": [1, 2, 3]},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["group_id"] == 1
            assert data["removed_count"] == 2
            assert data["not_member_count"] == 1
            assert data["errors"] == []

            # サービスメソッドが正しく呼ばれたことを確認
            remove_method = MembershipService.remove_multiple_members_from_group
            remove_method.assert_called_once_with(mock_db, 1, [1, 2, 3])
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_check_membership_true(self, client: TestClient):
        """メンバーシップ確認 - メンバーである"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（Trueを返す）
        MembershipService.is_member_of_group = MagicMock(return_value=True)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # メンバーシップ確認
            response = client.get("/api/memberships/users/1/groups/1/membership")

            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == 1
            assert data["group_id"] == 1
            assert data["is_member"] is True

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.is_member_of_group.assert_called_once_with(mock_db, 1, 1)
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_check_membership_false(self, client: TestClient):
        """メンバーシップ確認 - メンバーでない"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（Falseを返す）
        MembershipService.is_member_of_group = MagicMock(return_value=False)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # メンバーシップ確認
            response = client.get("/api/memberships/users/1/groups/1/membership")

            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == 1
            assert data["group_id"] == 1
            assert data["is_member"] is False

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.is_member_of_group.assert_called_once_with(mock_db, 1, 1)
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_add_member_to_group_internal_error(self, client: TestClient):
        """グループメンバー追加 - 内部エラー"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（例外を発生させる）
        MembershipService.add_member_to_group = MagicMock(
            side_effect=Exception("データベース接続エラー")
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # メンバー追加（内部エラー）
            response = client.post(
                "/api/memberships/", json={"user_id": 1, "group_id": 1}
            )

            assert response.status_code == 500
            assert (
                "メンバー追加処理中にエラーが発生しました" in response.json()["detail"]
            )

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.add_member_to_group.assert_called_once_with(mock_db, 1, 1)
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_remove_member_from_group_internal_error(self, client: TestClient):
        """グループメンバー削除 - 内部エラー"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（例外を発生させる）
        MembershipService.remove_member_from_group = MagicMock(
            side_effect=Exception("データベース接続エラー")
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # メンバー削除（内部エラー）
            response = client.delete("/api/memberships/groups/1/users/1")

            assert response.status_code == 500
            assert (
                "メンバー削除処理中にエラーが発生しました" in response.json()["detail"]
            )

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.remove_member_from_group.assert_called_once_with(
                mock_db, 1, 1
            )
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_get_group_members_internal_error(self, client: TestClient):
        """グループメンバー一覧取得 - 内部エラー"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（例外を発生させる）
        MembershipService.get_group_members = MagicMock(
            side_effect=Exception("データベース接続エラー")
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # グループメンバー一覧取得（内部エラー）
            response = client.get("/api/memberships/groups/1/members")

            assert response.status_code == 500
            assert (
                "グループメンバー取得処理中にエラーが発生しました"
                in response.json()["detail"]
            )

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.get_group_members.assert_called_once_with(
                mock_db, 1, False
            )
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_get_user_groups_internal_error(self, client: TestClient):
        """ユーザー所属グループ一覧取得 - 内部エラー"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（例外を発生させる）
        MembershipService.get_user_groups = MagicMock(
            side_effect=Exception("データベース接続エラー")
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # ユーザー所属グループ一覧取得（内部エラー）
            response = client.get("/api/memberships/users/1/groups")

            assert response.status_code == 500
            assert (
                "ユーザーグループ取得処理中にエラーが発生しました"
                in response.json()["detail"]
            )

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.get_user_groups.assert_called_once_with(mock_db, 1, False)
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_add_multiple_members_to_group_internal_error(self, client: TestClient):
        """複数メンバー一括追加 - 内部エラー"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（例外を発生させる）
        MembershipService.add_multiple_members_to_group = MagicMock(
            side_effect=Exception("データベース接続エラー")
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # 複数メンバー一括追加（内部エラー）
            response = client.post(
                "/api/memberships/bulk-add", json={"group_id": 1, "user_ids": [1, 2]}
            )

            assert response.status_code == 500
            assert (
                "一括メンバー追加処理中にエラーが発生しました"
                in response.json()["detail"]
            )

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.add_multiple_members_to_group.assert_called_once_with(
                mock_db, 1, [1, 2]
            )
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_remove_multiple_members_from_group_internal_error(
        self, client: TestClient
    ):
        """複数メンバー一括削除 - 内部エラー"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（例外を発生させる）
        MembershipService.remove_multiple_members_from_group = MagicMock(
            side_effect=Exception("データベース接続エラー")
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # 複数メンバー一括削除（内部エラー）
            response = client.post(
                "/api/memberships/bulk-remove", json={"group_id": 1, "user_ids": [1, 2]}
            )

            assert response.status_code == 500
            assert (
                "一括メンバー削除処理中にエラーが発生しました"
                in response.json()["detail"]
            )

            # サービスメソッドが正しく呼ばれたことを確認
            remove_method = MembershipService.remove_multiple_members_from_group
            remove_method.assert_called_once_with(mock_db, 1, [1, 2])
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_check_membership_internal_error(self, client: TestClient):
        """メンバーシップ確認 - 内部エラー"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（例外を発生させる）
        MembershipService.is_member_of_group = MagicMock(
            side_effect=Exception("データベース接続エラー")
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # メンバーシップ確認（内部エラー）
            response = client.get("/api/memberships/users/1/groups/1/membership")

            assert response.status_code == 500
            assert (
                "メンバーシップ確認処理中にエラーが発生しました"
                in response.json()["detail"]
            )

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.is_member_of_group.assert_called_once_with(mock_db, 1, 1)
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_add_member_to_group_http_exception(self, client: TestClient):
        """グループメンバー追加 - HTTPException再発生"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（HTTPExceptionを発生させる）
        from fastapi import HTTPException, status

        MembershipService.add_member_to_group = MagicMock(
            side_effect=HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="既にメンバーです"
            )
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # メンバー追加（HTTPException）
            response = client.post(
                "/api/memberships/", json={"user_id": 1, "group_id": 1}
            )

            assert response.status_code == 409
            assert "既にメンバーです" in response.json()["detail"]

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.add_member_to_group.assert_called_once_with(mock_db, 1, 1)
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_get_group_members_http_exception(self, client: TestClient):
        """グループメンバー一覧取得 - HTTPException再発生"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（HTTPExceptionを発生させる）
        from fastapi import HTTPException, status

        MembershipService.get_group_members = MagicMock(
            side_effect=HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="アクセス権限がありません"
            )
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # グループメンバー一覧取得（HTTPException）
            response = client.get("/api/memberships/groups/1/members")

            assert response.status_code == 403
            assert "アクセス権限がありません" in response.json()["detail"]

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.get_group_members.assert_called_once_with(
                mock_db, 1, False
            )
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_get_user_groups_http_exception(self, client: TestClient):
        """ユーザー所属グループ一覧取得 - HTTPException再発生"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（HTTPExceptionを発生させる）
        from fastapi import HTTPException, status

        MembershipService.get_user_groups = MagicMock(
            side_effect=HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="アクセス権限がありません"
            )
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # ユーザー所属グループ一覧取得（HTTPException）
            response = client.get("/api/memberships/users/1/groups")

            assert response.status_code == 403
            assert "アクセス権限がありません" in response.json()["detail"]

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.get_user_groups.assert_called_once_with(mock_db, 1, False)
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_add_multiple_members_to_group_http_exception(self, client: TestClient):
        """複数メンバー一括追加 - HTTPException再発生"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（HTTPExceptionを発生させる）
        from fastapi import HTTPException, status

        MembershipService.add_multiple_members_to_group = MagicMock(
            side_effect=HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="アクセス権限がありません"
            )
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # 複数メンバー一括追加（HTTPException）
            response = client.post(
                "/api/memberships/bulk-add", json={"group_id": 1, "user_ids": [1, 2]}
            )

            assert response.status_code == 403
            assert "アクセス権限がありません" in response.json()["detail"]

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.add_multiple_members_to_group.assert_called_once_with(
                mock_db, 1, [1, 2]
            )
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_remove_multiple_members_from_group_http_exception(
        self, client: TestClient
    ):
        """複数メンバー一括削除 - HTTPException再発生"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（HTTPExceptionを発生させる）
        from fastapi import HTTPException, status

        MembershipService.remove_multiple_members_from_group = MagicMock(
            side_effect=HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="アクセス権限がありません"
            )
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # 複数メンバー一括削除（HTTPException）
            response = client.post(
                "/api/memberships/bulk-remove", json={"group_id": 1, "user_ids": [1, 2]}
            )

            assert response.status_code == 403
            assert "アクセス権限がありません" in response.json()["detail"]

            # サービスメソッドが正しく呼ばれたことを確認
            remove_method = MembershipService.remove_multiple_members_from_group
            remove_method.assert_called_once_with(mock_db, 1, [1, 2])
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()

    def test_check_membership_http_exception(self, client: TestClient):
        """メンバーシップ確認 - HTTPException再発生"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # MembershipServiceのメソッドをモック化（HTTPExceptionを発生させる）
        from fastapi import HTTPException, status

        MembershipService.is_member_of_group = MagicMock(
            side_effect=HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="アクセス権限がありません"
            )
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # メンバーシップ確認（HTTPException）
            response = client.get("/api/memberships/users/1/groups/1/membership")

            assert response.status_code == 403
            assert "アクセス権限がありません" in response.json()["detail"]

            # サービスメソッドが正しく呼ばれたことを確認
            MembershipService.is_member_of_group.assert_called_once_with(mock_db, 1, 1)
        finally:
            # 依存性クリア
            app.dependency_overrides.clear()
