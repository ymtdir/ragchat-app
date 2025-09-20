"""
MembershipServiceの直接テストモジュール

テスト実行方法:
1. コマンドラインからの実行:
    python -m pytest -v tests/
    python -m pytest -v tests/test_membership_service.py

2. 特定のテストメソッドだけ実行:
    python -m pytest -v \
        tests/test_membership_service.py::TestMembershipServiceDirect::test_add_member_to_group_success

3. カバレッジレポート生成:
    coverage run -m pytest tests/test_membership_service.py
    coverage report
    coverage html
"""

import pytest
from unittest.mock import MagicMock, patch

from app.models.membership import Membership
from app.models.user import User
from app.models.group import Group
from app.services.memberships import MembershipService


class TestMembershipServiceDirect:
    """MembershipServiceの直接テストクラス"""

    def test_add_member_to_group_success(self):
        """グループにメンバーを追加する正常系テスト"""
        mock_db = MagicMock()
        mock_group = Group(id=1, name="testgroup", description="テストグループ")
        mock_user = User(id=1, name="testuser", email="test@example.com")
        mock_membership = Membership(id=1, user_id=1, group_id=1)

        # グループとユーザーの存在確認をモック
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_group,
            mock_user,
            None,
        ]
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        with patch("app.services.memberships.Membership", return_value=mock_membership):
            with patch("app.services.memberships.and_"):
                result = MembershipService.add_member_to_group(mock_db, 1, 1)

                assert result is not None
                assert result.user_id == 1
                assert result.group_id == 1
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
                mock_db.refresh.assert_called_once_with(result)

    def test_add_member_to_group_group_not_found(self):
        """存在しないグループにメンバーを追加するテスト"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="ID 1 のグループが見つかりません"):
            MembershipService.add_member_to_group(mock_db, 1, 1)

    def test_add_member_to_group_user_not_found(self):
        """存在しないユーザーをグループに追加するテスト"""
        mock_db = MagicMock()
        mock_group = Group(id=1, name="testgroup", description="テストグループ")
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_group,
            None,
        ]

        with pytest.raises(ValueError, match="ID 1 のユーザーが見つかりません"):
            MembershipService.add_member_to_group(mock_db, 1, 1)

    def test_add_member_to_group_already_member(self):
        """既にメンバーのユーザーを追加するテスト"""
        mock_db = MagicMock()
        mock_group = Group(id=1, name="testgroup", description="テストグループ")
        mock_user = User(id=1, name="testuser", email="test@example.com")
        mock_existing = Membership(id=1, user_id=1, group_id=1)

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_group,
            mock_user,
            mock_existing,
        ]

        with pytest.raises(
            ValueError, match="ユーザーは既にこのグループのメンバーです"
        ):
            MembershipService.add_member_to_group(mock_db, 1, 1)

    def test_remove_member_from_group_success(self):
        """グループからメンバーを削除する正常系テスト"""
        mock_db = MagicMock()
        mock_membership = Membership(id=1, user_id=1, group_id=1)
        mock_membership.soft_delete = MagicMock()

        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_membership
        )
        mock_db.commit.return_value = None

        result = MembershipService.remove_member_from_group(mock_db, 1, 1)

        assert result is True
        mock_membership.soft_delete.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_remove_member_from_group_not_found(self):
        """存在しないメンバーシップを削除するテスト"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(
            ValueError, match="指定されたメンバーシップが見つかりません"
        ):
            MembershipService.remove_member_from_group(mock_db, 1, 1)

    def test_get_group_members_empty(self):
        """グループのメンバー一覧取得の空結果テスト"""
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value.join.return_value.filter.return_value
        mock_query.all.return_value = []

        result = MembershipService.get_group_members(mock_db, 1)

        assert result is not None
        assert len(result) == 0

    def test_get_user_groups_empty(self):
        """ユーザーの所属グループ一覧取得の空結果テスト"""
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value.join.return_value.filter.return_value
        mock_query.all.return_value = []

        result = MembershipService.get_user_groups(mock_db, 1)

        assert result is not None
        assert len(result) == 0

    def test_add_multiple_members_to_group_success(self):
        """グループに複数のメンバーを一括追加する正常系テスト"""
        mock_db = MagicMock()
        mock_group = Group(id=1, name="testgroup", description="テストグループ")
        mock_user1 = User(id=1, name="user1", email="user1@example.com")
        mock_user2 = User(id=2, name="user2", email="user2@example.com")

        # グループの存在確認
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_group]
        # ユーザーの存在確認（2回）
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_group,
            mock_user1,
            mock_user2,
        ]
        # 既存メンバーシップの確認（2回、どちらもNone）
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_group,
            mock_user1,
            None,
            mock_user2,
            None,
        ]

        mock_db.add.return_value = None
        mock_db.commit.return_value = None

        with patch("app.services.memberships.Membership", return_value=Membership()):
            with patch("app.services.memberships.and_"):
                result = MembershipService.add_multiple_members_to_group(
                    mock_db, 1, [1, 2]
                )

                assert result is not None
                assert result["added_count"] == 2
                assert result["already_member_count"] == 0
                assert len(result["errors"]) == 0
                mock_db.commit.assert_called_once()

    def test_add_multiple_members_to_group_group_not_found(self):
        """存在しないグループに複数のメンバーを追加するテスト"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="ID 1 のグループが見つかりません"):
            MembershipService.add_multiple_members_to_group(mock_db, 1, [1, 2])

    def test_remove_multiple_members_from_group_success(self):
        """グループから複数のメンバーを一括削除する正常系テスト"""
        mock_db = MagicMock()
        mock_membership1 = Membership(id=1, user_id=1, group_id=1)
        mock_membership2 = Membership(id=2, user_id=2, group_id=1)
        mock_membership1.soft_delete = MagicMock()
        mock_membership2.soft_delete = MagicMock()

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_membership1,
            mock_membership2,
        ]
        mock_db.commit.return_value = None

        result = MembershipService.remove_multiple_members_from_group(
            mock_db, 1, [1, 2]
        )

        assert result is not None
        assert result["removed_count"] == 2
        assert result["not_member_count"] == 0
        assert len(result["errors"]) == 0
        mock_db.commit.assert_called_once()

    def test_remove_multiple_members_from_group_partial_success(self):
        """グループから複数のメンバーを一括削除する部分成功テスト"""
        mock_db = MagicMock()
        mock_membership1 = Membership(id=1, user_id=1, group_id=1)
        mock_membership1.soft_delete = MagicMock()

        # 1つ目のメンバーシップは存在、2つ目は存在しない
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_membership1,
            None,
        ]
        mock_db.commit.return_value = None

        result = MembershipService.remove_multiple_members_from_group(
            mock_db, 1, [1, 2]
        )

        assert result is not None
        assert result["removed_count"] == 1
        assert result["not_member_count"] == 1
        assert len(result["errors"]) == 0
        mock_db.commit.assert_called_once()

    def test_is_member_of_group_true(self):
        """ユーザーがグループのメンバーかどうかの確認テスト（メンバーの場合）"""
        mock_db = MagicMock()
        mock_membership = Membership(id=1, user_id=1, group_id=1)
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_membership
        )

        result = MembershipService.is_member_of_group(mock_db, 1, 1)

        assert result is True

    def test_is_member_of_group_false(self):
        """ユーザーがグループのメンバーかどうかの確認テスト（メンバーでない場合）"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = MembershipService.is_member_of_group(mock_db, 1, 1)

        assert result is False

    def test_add_multiple_members_to_group_user_not_found_real_implementation(self):
        """存在しないユーザーをグループに追加するテスト（実装テスト）"""
        mock_db = MagicMock()
        mock_group = Group(id=1, name="testgroup", description="テストグループ")

        # グループの存在確認
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_group]
        # ユーザーの存在確認（存在しない）
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_group,
            None,
        ]

        mock_db.commit.return_value = None

        with patch("app.services.memberships.Membership", return_value=Membership()):
            with patch("app.services.memberships.and_"):
                result = MembershipService.add_multiple_members_to_group(
                    mock_db, 1, [999]
                )

                assert result is not None
                assert result["added_count"] == 0
                assert result["already_member_count"] == 0
                assert len(result["errors"]) == 1
                assert "ID 999 のユーザーが見つかりません" in result["errors"][0]
                mock_db.commit.assert_called_once()

    def test_add_multiple_members_to_group_already_member_real_implementation(self):
        """既にメンバーのユーザーをグループに追加するテスト（実装テスト）"""
        mock_db = MagicMock()
        mock_group = Group(id=1, name="testgroup", description="テストグループ")
        mock_user = User(id=1, name="user1", email="user1@example.com")
        mock_existing = Membership(id=1, user_id=1, group_id=1)

        # グループの存在確認
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_group]
        # ユーザーの存在確認
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_group,
            mock_user,
        ]
        # 既存メンバーシップの確認（存在する）
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_group,
            mock_user,
            mock_existing,
        ]

        mock_db.commit.return_value = None

        with patch("app.services.memberships.Membership", return_value=Membership()):
            with patch("app.services.memberships.and_"):
                result = MembershipService.add_multiple_members_to_group(
                    mock_db, 1, [1]
                )

                assert result is not None
                assert result["added_count"] == 0
                assert result["already_member_count"] == 1
                assert len(result["errors"]) == 0
                mock_db.commit.assert_called_once()

    def test_remove_multiple_members_from_group_error_real_implementation(self):
        """複数メンバー削除時のエラーテスト（実装テスト）"""
        mock_db = MagicMock()
        mock_membership = Membership(id=1, user_id=1, group_id=1)
        mock_membership.soft_delete = MagicMock(side_effect=Exception("削除エラー"))

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_membership
        ]
        mock_db.commit.return_value = None

        result = MembershipService.remove_multiple_members_from_group(mock_db, 1, [1])

        assert result is not None
        assert result["removed_count"] == 0
        assert result["not_member_count"] == 0
        assert len(result["errors"]) == 1
        assert "ユーザー 1 の削除に失敗: 削除エラー" in result["errors"][0]
        mock_db.commit.assert_called_once()

    def test_add_multiple_members_to_group_error_real_implementation(self):
        """複数メンバー追加時のエラーテスト（実装テスト）"""
        mock_db = MagicMock()
        mock_group = Group(id=1, name="testgroup", description="テストグループ")
        mock_user = User(id=1, name="user1", email="user1@example.com")

        # グループの存在確認
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_group]
        # ユーザーの存在確認
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_group,
            mock_user,
        ]
        # 既存メンバーシップの確認（存在しない）
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_group,
            mock_user,
            None,
        ]

        mock_db.add.side_effect = Exception("追加エラー")
        mock_db.commit.return_value = None

        with patch("app.services.memberships.Membership", return_value=Membership()):
            with patch("app.services.memberships.and_"):
                result = MembershipService.add_multiple_members_to_group(
                    mock_db, 1, [1]
                )

                assert result is not None
                assert result["added_count"] == 0
                assert result["already_member_count"] == 0
                assert len(result["errors"]) == 1
                assert "ユーザー 1 の追加に失敗: 追加エラー" in result["errors"][0]
                mock_db.commit.assert_called_once()
