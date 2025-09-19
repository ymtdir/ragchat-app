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

import pytest
from unittest.mock import MagicMock
from datetime import datetime
from fastapi.testclient import TestClient

from app.models.user import User
from app.models.group import Group
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
            # 依存性オーバーライドをクリア
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
            # 依存性オーバーライドをクリア
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
            # 依存性オーバーライドをクリア
            app.dependency_overrides.clear()
