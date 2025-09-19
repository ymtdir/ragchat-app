"""
GroupServiceの直接テストモジュール

テスト実行方法:
1. コマンドラインからの実行:
   python -m pytest -v tests/
   python -m pytest -v tests/test_group_service.py

2. 特定のテストメソッドだけ実行:
   python -m pytest -v \
       tests/test_group_service.py::TestGroupServiceDirect::test_create_group_success

3. カバレッジレポート生成:
   coverage run -m pytest tests/test_group_service.py
   coverage report
   coverage html
"""

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.group import Group
from app.services.groups import GroupService
from app.schemas.groups import GroupCreate, GroupUpdate


class TestGroupServiceDirect:
    """GroupServiceの直接テストクラス"""

    def test_create_group_success(self):
        """グループ作成の正常系テスト"""
        mock_db = MagicMock()
        group_data = GroupCreate(name="testgroup", description="テストグループ")
        mock_group = Group(
            id=1,
            name="testgroup",
            description="テストグループ",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        with patch("app.services.groups.Group", return_value=mock_group):
            created_group = GroupService.create_group(mock_db, group_data)

            assert created_group is not None
            assert created_group.name == "testgroup"
            assert created_group.description == "テストグループ"
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(created_group)

    def test_create_group_duplicate_name(self):
        """グループ作成時の名前重複エラーテスト"""
        mock_db = MagicMock()
        group_data = GroupCreate(name="testgroup", description="テストグループ")
        mock_db.add.side_effect = IntegrityError(
            "UNIQUE constraint failed: groups.name", "", ""
        )
        mock_db.rollback.return_value = None

        with patch("app.services.groups.Group", return_value=Group()):
            with pytest.raises(
                IntegrityError, match="グループ名が既に使用されています"
            ):
                GroupService.create_group(mock_db, group_data)

            mock_db.add.assert_called_once()
            mock_db.rollback.assert_called_once()

    def test_create_group_other_integrity_error(self):
        """グループ作成時のその他のIntegrityErrorテスト"""
        mock_db = MagicMock()
        group_data = GroupCreate(name="testgroup", description="テストグループ")
        mock_db.add.side_effect = IntegrityError("Other constraint failed", "", "")
        mock_db.rollback.return_value = None

        with patch("app.services.groups.Group", return_value=Group()):
            with pytest.raises(IntegrityError, match="Other constraint failed"):
                GroupService.create_group(mock_db, group_data)

            mock_db.add.assert_called_once()
            mock_db.rollback.assert_called_once()

    def test_get_all_groups_success(self):
        """全グループ取得の正常系テスト"""
        mock_db = MagicMock()
        mock_groups = [
            Group(id=1, name="group1", description="グループ1"),
            Group(id=2, name="group2", description="グループ2"),
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_groups

        result = GroupService.get_all_groups(mock_db)

        assert result is not None
        assert len(result) == 2
        mock_db.query.assert_called_once()

    def test_get_all_groups_empty(self):
        """全グループ取得の空結果テスト"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        result = GroupService.get_all_groups(mock_db)

        assert result is not None
        assert len(result) == 0
        mock_db.query.assert_called_once()

    def test_get_all_groups_include_deleted(self):
        """削除済みを含む全グループ取得のテスト"""
        mock_db = MagicMock()
        mock_groups = [
            Group(id=1, name="group1", description="グループ1"),
            Group(id=2, name="group2", description="グループ2"),
        ]
        mock_db.query.return_value.all.return_value = mock_groups

        result = GroupService.get_all_groups(mock_db, include_deleted=True)

        assert result is not None
        assert len(result) == 2
        mock_db.query.assert_called_once()

    def test_is_name_taken_true(self):
        """グループ名重複チェックの重複ありテスト"""
        mock_db = MagicMock()
        mock_group = Group(id=1, name="testgroup")
        mock_db.query.return_value.filter.return_value.first.return_value = mock_group

        result = GroupService.is_name_taken(mock_db, "testgroup")

        assert result is True
        mock_db.query.assert_called_once()

    def test_update_group_duplicate_name(self):
        """グループ更新時の名前重複テスト"""
        mock_db = MagicMock()
        mock_group = Group(
            id=1,
            name="testgroup",
            description="テストグループ",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_group

        with patch.object(GroupService, "is_name_taken", return_value=True):
            update_data = GroupUpdate(name="duplicategroup")

            with pytest.raises(
                IntegrityError, match="グループ名が既に使用されています"
            ):
                GroupService.update_group(mock_db, 1, update_data)

    def test_soft_delete_group_by_id_success(self):
        """グループ論理削除の正常系テスト"""
        mock_db = MagicMock()
        mock_group = Group(
            id=1,
            name="testgroup",
            description="テストグループ",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        # deleted_at属性を設定可能にする
        mock_group.deleted_at = None
        mock_db.query.return_value.filter.return_value.first.return_value = mock_group
        mock_db.commit.return_value = None

        result = GroupService.soft_delete_group_by_id(mock_db, 1)

        assert result is True
        # deleted_atが設定されたことを確認
        assert hasattr(mock_group, "deleted_at")
        mock_db.commit.assert_called_once()

    def test_hard_delete_group_by_id_success(self):
        """グループ物理削除の正常系テスト"""
        mock_db = MagicMock()
        mock_group = Group(
            id=1,
            name="testgroup",
            description="テストグループ",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_group
        mock_db.delete.return_value = None
        mock_db.commit.return_value = None

        result = GroupService.hard_delete_group_by_id(mock_db, 1)

        assert result is True
        mock_db.delete.assert_called_once_with(mock_group)
        mock_db.commit.assert_called_once()

    def test_hard_delete_group_by_id_not_found(self):
        """存在しないグループの物理削除テスト"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = GroupService.hard_delete_group_by_id(mock_db, 999)

        assert result is False
        mock_db.query.assert_called_once()

    def test_restore_group_by_id_success(self):
        """グループ復元の正常系テスト"""
        mock_db = MagicMock()
        mock_group = Group(
            id=1,
            name="testgroup",
            description="テストグループ",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=datetime.now(),  # 削除済み
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_group
        mock_db.commit.return_value = None

        result = GroupService.restore_group_by_id(mock_db, 1)

        assert result is True
        assert mock_group.deleted_at is None
        mock_db.commit.assert_called_once()

    def test_restore_group_by_id_not_found(self):
        """存在しないグループの復元テスト"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = GroupService.restore_group_by_id(mock_db, 999)

        assert result is False
        mock_db.query.assert_called_once()

    def test_restore_group_by_id_not_deleted(self):
        """削除されていないグループの復元テスト"""
        mock_db = MagicMock()
        mock_group = Group(
            id=1,
            name="testgroup",
            description="テストグループ",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=None,  # 削除されていない
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_group

        result = GroupService.restore_group_by_id(mock_db, 1)

        assert result is False
        mock_db.query.assert_called_once()

    def test_soft_delete_all_groups_success(self):
        """全グループ論理削除の正常系テスト"""
        mock_db = MagicMock()
        mock_groups = [
            Group(id=1, name="group1", description="グループ1"),
            Group(id=2, name="group2", description="グループ2"),
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_groups
        mock_db.commit.return_value = None

        deleted_count = GroupService.soft_delete_all_groups(mock_db)

        assert deleted_count == 2
        assert all(group.deleted_at is not None for group in mock_groups)
        mock_db.commit.assert_called_once()

    def test_soft_delete_all_groups_empty(self):
        """全グループ論理削除の空結果テスト"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        deleted_count = GroupService.soft_delete_all_groups(mock_db)

        assert deleted_count == 0
        mock_db.query.assert_called_once()

    def test_delete_group_by_id_alias_success(self):
        """グループ削除のエイリアスメソッドの正常系テスト"""
        mock_db = MagicMock()
        mock_group = Group(
            id=1,
            name="testgroup",
            description="テストグループ",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        # deleted_at属性を設定可能にする
        mock_group.deleted_at = None
        mock_db.query.return_value.filter.return_value.first.return_value = mock_group
        mock_db.commit.return_value = None

        result = GroupService.delete_group_by_id(mock_db, 1)

        assert result is True
        # deleted_atが設定されたことを確認
        assert hasattr(mock_group, "deleted_at")
        mock_db.commit.assert_called_once()

    def test_delete_all_groups_alias_success(self):
        """全グループ削除のエイリアスメソッドの正常系テスト"""
        mock_db = MagicMock()
        mock_groups = [
            Group(id=1, name="group1", description="グループ1"),
            Group(id=2, name="group2", description="グループ2"),
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_groups
        mock_db.commit.return_value = None

        deleted_count = GroupService.delete_all_groups(mock_db)

        assert deleted_count == 2
        assert all(group.deleted_at is not None for group in mock_groups)
        mock_db.commit.assert_called_once()

    def test_delete_all_groups_alias_empty(self):
        """全グループ削除のエイリアスメソッドの空結果テスト"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        deleted_count = GroupService.delete_all_groups(mock_db)

        assert deleted_count == 0
        mock_db.query.assert_called_once()
