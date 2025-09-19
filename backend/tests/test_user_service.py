"""
UserServiceの直接テストモジュール

テスト実行方法:
1. コマンドラインからの実行:
    python -m pytest -v tests/
    python -m pytest -v tests/test_user_service.py

2. 特定のテストメソッドだけ実行:
    python -m pytest -v \
        tests/test_user_service.py::TestUserServiceDirect::test_create_user_success

3. カバレッジレポート生成:
    coverage run -m pytest tests/test_user_service.py
    coverage report
    coverage html
"""

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.user import User
from app.services.users import UserService
from app.schemas.users import UserCreate, UserUpdate


class TestUserServiceDirect:
    """UserServiceの直接テストクラス（モック使用）"""

    def test_create_user_success(self):
        """ユーザー作成の正常系テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=None,
        )

        # UserService.create_userをモック
        with patch.object(UserService, "create_user") as mock_create:
            mock_create.return_value = mock_user

            # テストデータ
            user_data = UserCreate(
                name="testuser", email="test@example.com", password="password123"
            )

            # ユーザーを作成
            created_user = UserService.create_user(mock_db, user_data)

            # 検証
            assert created_user is not None
            assert created_user.name == "testuser"
            assert created_user.email == "test@example.com"
            assert created_user.id == 1
            mock_create.assert_called_once_with(mock_db, user_data)

    def test_get_user_by_id_success(self):
        """IDでユーザー取得の正常系テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=None,
        )

        # UserService.get_user_by_idをモック
        with patch.object(UserService, "get_user_by_id") as mock_get:
            mock_get.return_value = mock_user

            # IDでユーザーを取得
            retrieved_user = UserService.get_user_by_id(mock_db, 1)

            # 検証
            assert retrieved_user is not None
            assert retrieved_user.id == 1
            assert retrieved_user.name == "testuser"
            assert retrieved_user.email == "test@example.com"
            mock_get.assert_called_once_with(mock_db, 1)

    def test_get_user_by_id_not_found(self):
        """IDでユーザー取得の異常系テスト（存在しないユーザー）"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.get_user_by_idをモック
        with patch.object(UserService, "get_user_by_id") as mock_get:
            mock_get.return_value = None

            # 存在しないIDでユーザーを取得
            retrieved_user = UserService.get_user_by_id(mock_db, 999)

            # 検証
            assert retrieved_user is None
            mock_get.assert_called_once_with(mock_db, 999)

    def test_get_user_by_name_success(self):
        """名前でユーザー取得の正常系テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=None,
        )

        # UserService.get_user_by_nameをモック
        with patch.object(UserService, "get_user_by_name") as mock_get:
            mock_get.return_value = mock_user

            # 名前でユーザーを取得
            retrieved_user = UserService.get_user_by_name(mock_db, "testuser")

            # 検証
            assert retrieved_user is not None
            assert retrieved_user.name == "testuser"
            assert retrieved_user.email == "test@example.com"
            mock_get.assert_called_once_with(mock_db, "testuser")

    def test_get_user_by_name_not_found(self):
        """名前でユーザー取得の異常系テスト（存在しないユーザー）"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.get_user_by_nameをモック
        with patch.object(UserService, "get_user_by_name") as mock_get:
            mock_get.return_value = None

            # 存在しない名前でユーザーを取得
            retrieved_user = UserService.get_user_by_name(mock_db, "nonexistent")

            # 検証
            assert retrieved_user is None
            mock_get.assert_called_once_with(mock_db, "nonexistent")

    def test_get_user_by_email_success(self):
        """メールアドレスでユーザー取得の正常系テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=None,
        )

        # UserService.get_user_by_emailをモック
        with patch.object(UserService, "get_user_by_email") as mock_get:
            mock_get.return_value = mock_user

            # メールアドレスでユーザーを取得
            retrieved_user = UserService.get_user_by_email(mock_db, "test@example.com")

            # 検証
            assert retrieved_user is not None
            assert retrieved_user.email == "test@example.com"
            assert retrieved_user.name == "testuser"
            mock_get.assert_called_once_with(mock_db, "test@example.com")

    def test_get_user_by_email_not_found(self):
        """メールアドレスでユーザー取得の異常系テスト（存在しないユーザー）"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.get_user_by_emailをモック
        with patch.object(UserService, "get_user_by_email") as mock_get:
            mock_get.return_value = None

            # 存在しないメールアドレスでユーザーを取得
            retrieved_user = UserService.get_user_by_email(
                mock_db, "nonexistent@example.com"
            )

            # 検証
            assert retrieved_user is None
            mock_get.assert_called_once_with(mock_db, "nonexistent@example.com")

    def test_get_all_users_success(self):
        """全ユーザー取得の正常系テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーリスト
        mock_users = [
            User(id=1, name="user1", email="user1@example.com", password="hash1"),
            User(id=2, name="user2", email="user2@example.com", password="hash2"),
            User(id=3, name="user3", email="user3@example.com", password="hash3"),
        ]

        # UserService.get_all_usersをモック
        with patch.object(UserService, "get_all_users") as mock_get:
            mock_get.return_value = mock_users

            # 全ユーザーを取得
            all_users = UserService.get_all_users(mock_db)

            # 検証
            assert len(all_users) == 3
            assert all_users[0].name == "user1"
            assert all_users[1].name == "user2"
            assert all_users[2].name == "user3"
            mock_get.assert_called_once_with(mock_db)

    def test_get_all_users_empty(self):
        """全ユーザー取得の異常系テスト（ユーザーなし）"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.get_all_usersをモック
        with patch.object(UserService, "get_all_users") as mock_get:
            mock_get.return_value = []

            # 全ユーザーを取得
            all_users = UserService.get_all_users(mock_db)

            # 検証
            assert len(all_users) == 0
            mock_get.assert_called_once_with(mock_db)

    def test_is_name_taken_always_false(self):
        """名前重複チェックのテスト（常にFalse）"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.is_name_takenをモック
        with patch.object(UserService, "is_name_taken") as mock_check:
            mock_check.return_value = False

            # 名前重複チェック
            result = UserService.is_name_taken(mock_db, "testuser")

            # 検証
            assert result is False
            mock_check.assert_called_once_with(mock_db, "testuser")

    def test_is_email_taken_true(self):
        """メールアドレス重複チェックの正常系テスト（重複あり）"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.is_email_takenをモック
        with patch.object(UserService, "is_email_taken") as mock_check:
            mock_check.return_value = True

            # メールアドレス重複チェック
            result = UserService.is_email_taken(mock_db, "test@example.com")

            # 検証
            assert result is True
            mock_check.assert_called_once_with(mock_db, "test@example.com")

    def test_is_email_taken_false(self):
        """メールアドレス重複チェックの正常系テスト（重複なし）"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.is_email_takenをモック
        with patch.object(UserService, "is_email_taken") as mock_check:
            mock_check.return_value = False

            # メールアドレス重複チェック
            result = UserService.is_email_taken(mock_db, "new@example.com")

            # 検証
            assert result is False
            mock_check.assert_called_once_with(mock_db, "new@example.com")

    def test_verify_password_success(self):
        """パスワード検証の正常系テスト"""
        # UserService.verify_passwordをモック
        with patch.object(UserService, "verify_password") as mock_verify:
            mock_verify.return_value = True

            # 正しいパスワードを検証
            result = UserService.verify_password("password123", "hashed_password")

            # 検証
            assert result is True
            mock_verify.assert_called_once_with("password123", "hashed_password")

    def test_verify_password_failure(self):
        """パスワード検証の異常系テスト"""
        # UserService.verify_passwordをモック
        with patch.object(UserService, "verify_password") as mock_verify:
            mock_verify.return_value = False

            # 間違ったパスワードを検証
            result = UserService.verify_password("wrongpassword", "hashed_password")

            # 検証
            assert result is False
            mock_verify.assert_called_once_with("wrongpassword", "hashed_password")

    def test_update_user_success(self):
        """ユーザー更新の正常系テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト
        mock_user = User(
            id=1,
            name="updateduser",
            email="updated@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=None,
        )

        # UserService.update_userをモック
        with patch.object(UserService, "update_user") as mock_update:
            mock_update.return_value = mock_user

            # ユーザー情報を更新
            update_data = UserUpdate(name="updateduser", email="updated@example.com")
            updated_user = UserService.update_user(mock_db, 1, update_data)

            # 検証
            assert updated_user is not None
            assert updated_user.name == "updateduser"
            assert updated_user.email == "updated@example.com"
            mock_update.assert_called_once_with(mock_db, 1, update_data)

    def test_update_user_not_found(self):
        """ユーザー更新の異常系テスト（存在しないユーザー）"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.update_userをモック
        with patch.object(UserService, "update_user") as mock_update:
            mock_update.return_value = None

            # 存在しないユーザーを更新
            update_data = UserUpdate(name="updateduser", email="updated@example.com")
            updated_user = UserService.update_user(mock_db, 999, update_data)

            # 検証
            assert updated_user is None
            mock_update.assert_called_once_with(mock_db, 999, update_data)

    def test_update_user_password_success(self):
        """ユーザーパスワード更新の正常系テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="new_hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=None,
        )

        # UserService.update_userをモック
        with patch.object(UserService, "update_user") as mock_update:
            mock_update.return_value = mock_user

            # パスワードを更新
            update_data = UserUpdate(
                current_password="password123", new_password="newpassword456"
            )
            updated_user = UserService.update_user(mock_db, 1, update_data)

            # 検証
            assert updated_user is not None
            assert updated_user.password == "new_hashed_password"
            mock_update.assert_called_once_with(mock_db, 1, update_data)

    def test_update_user_password_wrong_current(self):
        """ユーザーパスワード更新の異常系テスト（間違った現在のパスワード）"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.update_userをモック（ValueErrorを発生）
        with patch.object(UserService, "update_user") as mock_update:
            mock_update.side_effect = ValueError("現在のパスワードが正しくありません")

            # 間違った現在のパスワードで更新
            update_data = UserUpdate(
                current_password="wrongpassword", new_password="newpassword456"
            )

            # 検証（ValueErrorが発生することを確認）
            with pytest.raises(ValueError, match="現在のパスワードが正しくありません"):
                UserService.update_user(mock_db, 1, update_data)

    def test_update_user_password_missing_current(self):
        """ユーザー更新の異常系テスト（現在のパスワードなし）"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.update_userをモック（ValueErrorを発生）
        with patch.object(UserService, "update_user") as mock_update:
            mock_update.side_effect = ValueError(
                "パスワード変更には現在のパスワードが必要です"
            )

            # 現在のパスワードなしで更新
            update_data = UserUpdate(new_password="newpassword456")

            # 検証（ValueErrorが発生することを確認）
            with pytest.raises(
                ValueError, match="パスワード変更には現在のパスワードが必要です"
            ):
                UserService.update_user(mock_db, 1, update_data)

    def test_update_user_duplicate_email(self):
        """ユーザー更新の異常系テスト（重複するメールアドレス）"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.update_userをモック（IntegrityErrorを発生）
        with patch.object(UserService, "update_user") as mock_update:
            mock_update.side_effect = IntegrityError("", "", "")

            # 重複するメールアドレスで更新
            update_data = UserUpdate(email="existing@example.com")

            # 検証（IntegrityErrorが発生することを確認）
            with pytest.raises(IntegrityError):
                UserService.update_user(mock_db, 1, update_data)

    def test_soft_delete_user_by_id_success(self):
        """ユーザー論理削除の正常系テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.soft_delete_user_by_idをモック
        with patch.object(UserService, "soft_delete_user_by_id") as mock_delete:
            mock_delete.return_value = True

            # ユーザーを論理削除
            result = UserService.soft_delete_user_by_id(mock_db, 1)

            # 検証
            assert result is True
            mock_delete.assert_called_once_with(mock_db, 1)

    def test_soft_delete_user_by_id_not_found(self):
        """ユーザー論理削除の異常系テスト（存在しないユーザー）"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.soft_delete_user_by_idをモック
        with patch.object(UserService, "soft_delete_user_by_id") as mock_delete:
            mock_delete.return_value = False

            # 存在しないユーザーを論理削除
            result = UserService.soft_delete_user_by_id(mock_db, 999)

            # 検証
            assert result is False
            mock_delete.assert_called_once_with(mock_db, 999)

    def test_hard_delete_user_by_id_success(self):
        """ユーザー物理削除の正常系テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.hard_delete_user_by_idをモック
        with patch.object(UserService, "hard_delete_user_by_id") as mock_delete:
            mock_delete.return_value = True

            # ユーザーを物理削除
            result = UserService.hard_delete_user_by_id(mock_db, 1)

            # 検証
            assert result is True
            mock_delete.assert_called_once_with(mock_db, 1)

    def test_hard_delete_user_by_id_not_found(self):
        """ユーザー物理削除の異常系テスト（存在しないユーザー）"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.hard_delete_user_by_idをモック
        with patch.object(UserService, "hard_delete_user_by_id") as mock_delete:
            mock_delete.return_value = False

            # 存在しないユーザーを物理削除
            result = UserService.hard_delete_user_by_id(mock_db, 999)

            # 検証
            assert result is False
            mock_delete.assert_called_once_with(mock_db, 999)

    def test_restore_user_by_id_success(self):
        """ユーザー復元の正常系テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.restore_user_by_idをモック
        with patch.object(UserService, "restore_user_by_id") as mock_restore:
            mock_restore.return_value = True

            # ユーザーを復元
            result = UserService.restore_user_by_id(mock_db, 1)

            # 検証
            assert result is True
            mock_restore.assert_called_once_with(mock_db, 1)

    def test_restore_user_by_id_not_found(self):
        """ユーザー復元の異常系テスト（存在しないユーザー）"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.restore_user_by_idをモック
        with patch.object(UserService, "restore_user_by_id") as mock_restore:
            mock_restore.return_value = False

            # 存在しないユーザーを復元
            result = UserService.restore_user_by_id(mock_db, 999)

            # 検証
            assert result is False
            mock_restore.assert_called_once_with(mock_db, 999)

    def test_restore_user_by_id_not_deleted(self):
        """ユーザー復元の異常系テスト（削除されていないユーザー）"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.restore_user_by_idをモック
        with patch.object(UserService, "restore_user_by_id") as mock_restore:
            mock_restore.return_value = False

            # 削除されていないユーザーを復元
            result = UserService.restore_user_by_id(mock_db, 1)

            # 検証
            assert result is False
            mock_restore.assert_called_once_with(mock_db, 1)

    def test_soft_delete_all_users_success(self):
        """全ユーザー論理削除の正常系テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.soft_delete_all_usersをモック
        with patch.object(UserService, "soft_delete_all_users") as mock_delete:
            mock_delete.return_value = 3

            # 全ユーザーを論理削除
            deleted_count = UserService.soft_delete_all_users(mock_db)

            # 検証
            assert deleted_count == 3
            mock_delete.assert_called_once_with(mock_db)

    def test_soft_delete_all_users_empty(self):
        """全ユーザー論理削除の異常系テスト（ユーザーなし）"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.soft_delete_all_usersをモック
        with patch.object(UserService, "soft_delete_all_users") as mock_delete:
            mock_delete.return_value = 0

            # 全ユーザーを論理削除
            deleted_count = UserService.soft_delete_all_users(mock_db)

            # 検証
            assert deleted_count == 0
            mock_delete.assert_called_once_with(mock_db)

    def test_delete_user_by_id_alias_success(self):
        """ユーザー削除のエイリアスメソッドの正常系テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.delete_user_by_idをモック
        with patch.object(UserService, "delete_user_by_id") as mock_delete:
            mock_delete.return_value = True

            # エイリアスメソッドでユーザーを削除
            result = UserService.delete_user_by_id(mock_db, 1)

            # 検証
            assert result is True
            mock_delete.assert_called_once_with(mock_db, 1)

    def test_delete_user_by_id_alias_not_found(self):
        """ユーザー削除のエイリアスメソッドの異常系テスト（存在しないユーザー）"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.delete_user_by_idをモック
        with patch.object(UserService, "delete_user_by_id") as mock_delete:
            mock_delete.return_value = False

            # 存在しないユーザーを削除
            result = UserService.delete_user_by_id(mock_db, 999)

            # 検証
            assert result is False
            mock_delete.assert_called_once_with(mock_db, 999)

    def test_delete_all_users_alias_success(self):
        """全ユーザー削除のエイリアスメソッドの正常系テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.delete_all_usersをモック
        with patch.object(UserService, "delete_all_users") as mock_delete:
            mock_delete.return_value = 2

            # エイリアスメソッドで全ユーザーを削除
            deleted_count = UserService.delete_all_users(mock_db)

            # 検証
            assert deleted_count == 2
            mock_delete.assert_called_once_with(mock_db)

    def test_delete_all_users_alias_empty(self):
        """全ユーザー削除のエイリアスメソッドの異常系テスト（ユーザーなし）"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.delete_all_usersをモック
        with patch.object(UserService, "delete_all_users") as mock_delete:
            mock_delete.return_value = 0

            # エイリアスメソッドで全ユーザーを削除
            deleted_count = UserService.delete_all_users(mock_db)

            # 検証
            assert deleted_count == 0
            mock_delete.assert_called_once_with(mock_db)


class TestUserServiceImplementation:
    """UserServiceの実装テストクラス（モックベース）"""

    def test_create_user_implementation(self):
        """ユーザー作成の実装テスト"""
        from app.schemas.users import UserCreate

        # モックデータベースセッション
        mock_db = MagicMock()

        # テストデータ
        user_data = UserCreate(
            name="testuser", email="test@example.com", password="password123"
        )

        # モックユーザーオブジェクト
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=None,
        )

        # UserService.create_userをモック
        with patch.object(UserService, "create_user") as mock_create:
            mock_create.return_value = mock_user

            # ユーザーを作成
            created_user = UserService.create_user(mock_db, user_data)

            # 検証
            assert created_user is not None
            assert created_user.name == "testuser"
            assert created_user.email == "test@example.com"
            assert created_user.password == "hashed_password"
            assert created_user.id == 1
            assert created_user.created_at is not None
            assert created_user.updated_at is not None
            assert created_user.deleted_at is None
            mock_create.assert_called_once_with(mock_db, user_data)

    def test_create_user_duplicate_email(self):
        """重複メールアドレスでのユーザー作成テスト"""
        from app.schemas.users import UserCreate

        # モックデータベースセッション
        mock_db = MagicMock()

        # テストデータ
        user_data = UserCreate(
            name="user2", email="test@example.com", password="password456"
        )

        # UserService.create_userをモック（IntegrityErrorを発生）
        with patch.object(UserService, "create_user") as mock_create:
            mock_create.side_effect = IntegrityError("", "", "")

            # 同じメールアドレスでユーザーを作成（エラーが発生することを確認）
            with pytest.raises(IntegrityError):
                UserService.create_user(mock_db, user_data)

            mock_create.assert_called_once_with(mock_db, user_data)

    def test_get_user_by_id_implementation(self):
        """IDでユーザー取得の実装テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=None,
        )

        # UserService.get_user_by_idをモック
        with patch.object(UserService, "get_user_by_id") as mock_get:
            mock_get.return_value = mock_user

            # IDでユーザーを取得
            retrieved_user = UserService.get_user_by_id(mock_db, 1)

            # 検証
            assert retrieved_user is not None
            assert retrieved_user.id == 1
            assert retrieved_user.name == "testuser"
            assert retrieved_user.email == "test@example.com"
            mock_get.assert_called_once_with(mock_db, 1)

    def test_get_user_by_id_not_found_implementation(self):
        """存在しないIDでユーザー取得の実装テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.get_user_by_idをモック
        with patch.object(UserService, "get_user_by_id") as mock_get:
            mock_get.return_value = None

            # 存在しないIDでユーザーを取得
            retrieved_user = UserService.get_user_by_id(mock_db, 999)

            # 検証
            assert retrieved_user is None
            mock_get.assert_called_once_with(mock_db, 999)

    def test_get_user_by_name_implementation(self):
        """名前でユーザー取得の実装テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=None,
        )

        # UserService.get_user_by_nameをモック
        with patch.object(UserService, "get_user_by_name") as mock_get:
            mock_get.return_value = mock_user

            # 名前でユーザーを取得
            retrieved_user = UserService.get_user_by_name(mock_db, "testuser")

            # 検証
            assert retrieved_user is not None
            assert retrieved_user.name == "testuser"
            assert retrieved_user.email == "test@example.com"
            mock_get.assert_called_once_with(mock_db, "testuser")

    def test_get_user_by_email_implementation(self):
        """メールアドレスでユーザー取得の実装テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=None,
        )

        # UserService.get_user_by_emailをモック
        with patch.object(UserService, "get_user_by_email") as mock_get:
            mock_get.return_value = mock_user

            # メールアドレスでユーザーを取得
            retrieved_user = UserService.get_user_by_email(mock_db, "test@example.com")

            # 検証
            assert retrieved_user is not None
            assert retrieved_user.email == "test@example.com"
            assert retrieved_user.name == "testuser"
            mock_get.assert_called_once_with(mock_db, "test@example.com")

    def test_get_all_users_implementation(self):
        """全ユーザー取得の実装テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーリスト
        mock_users = [
            User(id=1, name="user1", email="user1@example.com", password="hash1"),
            User(id=2, name="user2", email="user2@example.com", password="hash2"),
            User(id=3, name="user3", email="user3@example.com", password="hash3"),
        ]

        # UserService.get_all_usersをモック
        with patch.object(UserService, "get_all_users") as mock_get:
            mock_get.return_value = mock_users

            # 全ユーザーを取得
            all_users = UserService.get_all_users(mock_db)

            # 検証
            assert len(all_users) == 3
            assert all_users[0].name == "user1"
            assert all_users[1].name == "user2"
            assert all_users[2].name == "user3"
            mock_get.assert_called_once_with(mock_db)

    def test_is_email_taken_implementation(self):
        """メールアドレス重複チェックの実装テスト"""
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserService.is_email_takenをモック
        with patch.object(UserService, "is_email_taken") as mock_check:
            mock_check.return_value = True

            # 同じメールアドレスで重複チェック
            result = UserService.is_email_taken(mock_db, "test@example.com")

            # 検証
            assert result is True
            mock_check.assert_called_once_with(mock_db, "test@example.com")

    def test_verify_password_implementation(self):
        """パスワード検証の実装テスト"""
        # UserService.verify_passwordをモック
        with patch.object(UserService, "verify_password") as mock_verify:
            mock_verify.return_value = True

            # 正しいパスワードを検証
            result = UserService.verify_password("password123", "hashed_password")

            # 検証
            assert result is True
            mock_verify.assert_called_once_with("password123", "hashed_password")

    def test_get_all_users_real_implementation(self):
        """全ユーザー取得の実装テスト（実際のメソッドを呼び出し）"""
        mock_db = MagicMock()
        mock_users = [
            User(id=1, name="user1", email="user1@example.com"),
            User(id=2, name="user2", email="user2@example.com"),
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_users

        result = UserService.get_all_users(mock_db)

        assert len(result) == 2
        assert result[0].name == "user1"
        assert result[1].name == "user2"
        mock_db.query.assert_called_once()

    def test_update_user_real_implementation(self):
        """ユーザー更新の実装テスト（実際のメソッドを呼び出し）"""
        mock_db = MagicMock()
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mock_db.commit.return_value = None

        # is_email_takenをモック（重複なし）
        with patch.object(UserService, "is_email_taken", return_value=False):
            update_data = UserUpdate(name="updateduser", email="updated@example.com")
            result = UserService.update_user(mock_db, 1, update_data)

            assert result is not None
            assert result.name == "updateduser"
            assert result.email == "updated@example.com"
            mock_db.commit.assert_called_once()

    def test_soft_delete_all_users_real_implementation(self):
        """全ユーザー論理削除の実装テスト（実際のメソッドを呼び出し）"""
        mock_db = MagicMock()
        mock_users = [
            User(id=1, name="user1", email="user1@example.com"),
            User(id=2, name="user2", email="user2@example.com"),
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_users
        mock_db.commit.return_value = None

        deleted_count = UserService.soft_delete_all_users(mock_db)

        assert deleted_count == 2
        assert all(user.deleted_at is not None for user in mock_users)
        mock_db.commit.assert_called_once()

    def test_verify_password_real_implementation(self):
        """パスワード検証の実装テスト（実際のメソッドを呼び出し）"""
        with patch("app.services.users.pwd_context.verify", return_value=True):
            result = UserService.verify_password("password123", "hashed_password")

            assert result is True

    def test_update_user_password_real_implementation(self):
        """ユーザーパスワード更新の実装テスト（実際のメソッドを呼び出し）"""
        mock_db = MagicMock()
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="old_hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mock_db.commit.return_value = None

        with patch.object(UserService, "verify_password", return_value=True):
            with patch(
                "app.services.users.pwd_context.hash",
                return_value="new_hashed_password",
            ):
                update_data = UserUpdate(
                    new_password="newpassword123", current_password="oldpassword123"
                )
                result = UserService.update_user(mock_db, 1, update_data)

                assert result is not None
                assert result.password == "new_hashed_password"
                mock_db.commit.assert_called_once()

    def test_update_user_password_wrong_current_real_implementation(self):
        """ユーザーパスワード更新時の現在のパスワードが間違っている場合のテスト"""
        mock_db = MagicMock()
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="old_hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        with patch.object(UserService, "verify_password", return_value=False):
            update_data = UserUpdate(
                new_password="newpassword123", current_password="wrongpassword"
            )

            with pytest.raises(ValueError, match="現在のパスワードが正しくありません"):
                UserService.update_user(mock_db, 1, update_data)

    def test_update_user_password_missing_current_real_implementation(self):
        """ユーザーパスワード更新時に現在のパスワードが提供されていない場合のテスト"""
        mock_db = MagicMock()
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="old_hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        update_data = UserUpdate(new_password="newpassword123")

        with pytest.raises(
            ValueError, match="パスワード変更には現在のパスワードが必要です"
        ):
            UserService.update_user(mock_db, 1, update_data)

    def test_update_user_duplicate_email_real_implementation(self):
        """ユーザー更新時のメールアドレス重複テスト"""
        mock_db = MagicMock()
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        with patch.object(UserService, "is_email_taken", return_value=True):
            update_data = UserUpdate(email="duplicate@example.com")

            with pytest.raises(
                IntegrityError, match="メールアドレスが既に使用されています"
            ):
                UserService.update_user(mock_db, 1, update_data)

    def test_hard_delete_user_by_id_real_implementation(self):
        """ユーザー物理削除の実装テスト（実際のメソッドを呼び出し）"""
        mock_db = MagicMock()
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mock_db.delete.return_value = None
        mock_db.commit.return_value = None

        result = UserService.hard_delete_user_by_id(mock_db, 1)

        assert result is True
        mock_db.delete.assert_called_once_with(mock_user)
        mock_db.commit.assert_called_once()

    def test_hard_delete_user_by_id_not_found_real_implementation(self):
        """存在しないユーザーの物理削除テスト"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = UserService.hard_delete_user_by_id(mock_db, 999)

        assert result is False
        mock_db.query.assert_called_once()

    def test_restore_user_by_id_real_implementation(self):
        """ユーザー復元の実装テスト（実際のメソッドを呼び出し）"""
        mock_db = MagicMock()
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=datetime.now(),  # 削除済み
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mock_db.commit.return_value = None

        result = UserService.restore_user_by_id(mock_db, 1)

        assert result is True
        assert mock_user.deleted_at is None
        mock_db.commit.assert_called_once()

    def test_restore_user_by_id_not_found_real_implementation(self):
        """存在しないユーザーの復元テスト"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = UserService.restore_user_by_id(mock_db, 999)

        assert result is False
        mock_db.query.assert_called_once()

    def test_restore_user_by_id_not_deleted_real_implementation(self):
        """削除されていないユーザーの復元テスト"""
        mock_db = MagicMock()
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=None,  # 削除されていない
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = UserService.restore_user_by_id(mock_db, 1)

        assert result is False
        mock_db.query.assert_called_once()

    def test_delete_all_users_alias_real_implementation(self):
        """全ユーザー削除のエイリアスメソッドの実装テスト"""
        mock_db = MagicMock()
        mock_users = [
            User(id=1, name="user1", email="user1@example.com"),
            User(id=2, name="user2", email="user2@example.com"),
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_users
        mock_db.commit.return_value = None

        deleted_count = UserService.delete_all_users(mock_db)

        assert deleted_count == 2
        assert all(user.deleted_at is not None for user in mock_users)
        mock_db.commit.assert_called_once()

    def test_delete_all_users_alias_empty_real_implementation(self):
        """全ユーザー削除のエイリアスメソッドの空の場合のテスト"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        deleted_count = UserService.delete_all_users(mock_db)

        assert deleted_count == 0
        mock_db.query.assert_called_once()

    def test_get_user_by_name_include_deleted_real_implementation(self):
        """削除済みユーザーを含む名前検索テスト（実装テスト）"""
        mock_db = MagicMock()
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_user.deleted_at = datetime.now()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = UserService.get_user_by_name(mock_db, "testuser", include_deleted=True)

        assert result is not None
        assert result.name == "testuser"
        mock_db.query.assert_called_once()

    def test_get_user_by_name_exclude_deleted_real_implementation(self):
        """削除済みユーザーを除外する名前検索テスト（実装テスト）"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            None
        )

        result = UserService.get_user_by_name(
            mock_db, "testuser", include_deleted=False
        )

        assert result is None
        mock_db.query.assert_called_once()

    def test_get_user_by_email_include_deleted_real_implementation(self):
        """削除済みユーザーを含むメール検索テスト（実装テスト）"""
        mock_db = MagicMock()
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_user.deleted_at = datetime.now()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = UserService.get_user_by_email(
            mock_db, "test@example.com", include_deleted=True
        )

        assert result is not None
        assert result.email == "test@example.com"
        mock_db.query.assert_called_once()

    def test_get_user_by_email_exclude_deleted_real_implementation(self):
        """削除済みユーザーを除外するメール検索テスト（実装テスト）"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            None
        )

        result = UserService.get_user_by_email(
            mock_db, "test@example.com", include_deleted=False
        )

        assert result is None
        mock_db.query.assert_called_once()

    def test_is_name_taken_real_implementation(self):
        """ユーザー名重複チェックテスト（実装テスト）"""
        mock_db = MagicMock()
        result = UserService.is_name_taken(mock_db, "testuser")

        assert result is False

    def test_update_user_not_found_real_implementation(self):
        """存在しないユーザーの更新テスト（実装テスト）"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            None
        )

        update_data = UserUpdate(name="updated_user")
        result = UserService.update_user(mock_db, 999, update_data)

        assert result is None
        mock_db.query.assert_called_once()

    def test_update_user_integrity_error_other_real_implementation(self):
        """ユーザー更新時のその他のIntegrityErrorテスト（実装テスト）"""
        mock_db = MagicMock()
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_db.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            mock_user
        )
        mock_db.commit.side_effect = IntegrityError(
            "UNIQUE constraint failed: users.name", "", ""
        )
        mock_db.rollback.return_value = None

        update_data = UserUpdate(name="duplicate_user")
        with pytest.raises(
            IntegrityError, match="UNIQUE constraint failed: users.name"
        ):
            UserService.update_user(mock_db, 1, update_data)

        mock_db.commit.assert_called_once()
        mock_db.rollback.assert_called_once()

    def test_soft_delete_user_by_id_success_real_implementation(self):
        """ユーザー論理削除の正常系テスト（実装テスト）"""
        mock_db = MagicMock()
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_user.soft_delete = MagicMock()
        mock_db.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            mock_user
        )
        mock_db.commit.return_value = None

        result = UserService.soft_delete_user_by_id(mock_db, 1)

        assert result is True
        mock_user.soft_delete.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_soft_delete_user_by_id_not_found_real_implementation(self):
        """存在しないユーザーの論理削除テスト（実装テスト）"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            None
        )

        result = UserService.soft_delete_user_by_id(mock_db, 999)

        assert result is False
        mock_db.query.assert_called_once()

    def test_soft_delete_user_by_id_exception_real_implementation(self):
        """ユーザー論理削除時の例外テスト（実装テスト）"""
        mock_db = MagicMock()
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_user.soft_delete = MagicMock(side_effect=Exception("削除エラー"))
        mock_db.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            mock_user
        )
        mock_db.rollback.return_value = None

        with pytest.raises(Exception, match="削除エラー"):
            UserService.soft_delete_user_by_id(mock_db, 1)

        mock_user.soft_delete.assert_called_once()
        mock_db.rollback.assert_called_once()

    def test_hard_delete_user_by_id_exception_real_implementation(self):
        """ユーザー物理削除時の例外テスト（実装テスト）"""
        mock_db = MagicMock()
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_db.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            mock_user
        )
        mock_db.delete.side_effect = Exception("削除エラー")
        mock_db.rollback.return_value = None

        with pytest.raises(Exception, match="削除エラー"):
            UserService.hard_delete_user_by_id(mock_db, 1)

        mock_db.rollback.assert_called_once()

    def test_soft_delete_all_users_exception_real_implementation(self):
        """全ユーザー論理削除時の例外テスト（実装テスト）"""
        mock_db = MagicMock()
        mock_users = [
            User(id=1, name="user1", email="user1@example.com"),
            User(id=2, name="user2", email="user2@example.com"),
        ]
        mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = (
            mock_users
        )
        mock_db.commit.side_effect = Exception("削除エラー")
        mock_db.rollback.return_value = None

        with pytest.raises(Exception, match="削除エラー"):
            UserService.soft_delete_all_users(mock_db)

        mock_db.commit.assert_called_once()
        mock_db.rollback.assert_called_once()

    def test_delete_user_by_id_alias_real_implementation(self):
        """ユーザー削除エイリアスメソッドテスト（実装テスト）"""
        mock_db = MagicMock()
        mock_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_user.soft_delete = MagicMock()
        mock_db.query.return_value.filter.return_value.filter.return_value.first.return_value = (
            mock_user
        )
        mock_db.commit.return_value = None

        result = UserService.delete_user_by_id(mock_db, 1)

        assert result is True
        mock_user.soft_delete.assert_called_once()
        mock_db.commit.assert_called_once()
