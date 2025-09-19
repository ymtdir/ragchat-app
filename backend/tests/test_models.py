"""
モデルクラスのテスト

User, Group, Membershipモデルの機能をテストします。
"""

from datetime import datetime, timezone
from app.models.user import User
from app.models.group import Group
from app.models.membership import Membership


class TestUserModel:
    """Userモデルのテストクラス"""

    def test_user_creation(self):
        """ユーザー作成のテスト"""
        user = User(
            name="testuser", email="test@example.com", password="hashed_password"
        )

        assert user.name == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "hashed_password"
        assert user.deleted_at is None

    def test_is_active_property_true(self):
        """is_activeプロパティ（True）のテスト"""
        user = User(
            name="testuser", email="test@example.com", password="hashed_password"
        )

        assert user.is_active is True
        assert user.is_deleted is False

    def test_is_active_property_false(self):
        """is_activeプロパティ（False）のテスト"""
        user = User(
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            deleted_at=datetime.now(timezone.utc),
        )

        assert user.is_active is False
        assert user.is_deleted is True

    def test_soft_delete(self):
        """論理削除のテスト"""
        user = User(
            name="testuser", email="test@example.com", password="hashed_password"
        )

        # 削除前の確認
        assert user.is_active is True
        assert user.deleted_at is None

        # 論理削除実行
        user.soft_delete()

        # 削除後の確認
        assert user.is_active is False
        assert user.deleted_at is not None
        assert isinstance(user.deleted_at, datetime)

    def test_repr_active_user(self):
        """__repr__メソッド（アクティブユーザー）のテスト"""
        user = User(
            id=1, name="testuser", email="test@example.com", password="hashed_password"
        )

        repr_str = repr(user)
        assert "User(id=1" in repr_str
        assert "name='testuser'" in repr_str
        assert "email='test@example.com'" in repr_str
        assert "status='active'" in repr_str

    def test_repr_deleted_user(self):
        """__repr__メソッド（削除済みユーザー）のテスト"""
        user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="hashed_password",
            deleted_at=datetime.now(timezone.utc),
        )

        repr_str = repr(user)
        assert "User(id=1" in repr_str
        assert "name='testuser'" in repr_str
        assert "email='test@example.com'" in repr_str
        assert "status='deleted'" in repr_str


class TestGroupModel:
    """Groupモデルのテストクラス"""

    def test_group_creation(self):
        """グループ作成のテスト"""
        group = Group(name="testgroup", description="Test group description")

        assert group.name == "testgroup"
        assert group.description == "Test group description"
        assert group.deleted_at is None

    def test_group_creation_without_description(self):
        """説明なしグループ作成のテスト"""
        group = Group(name="testgroup")

        assert group.name == "testgroup"
        assert group.description is None
        assert group.deleted_at is None

    def test_is_active_property_true(self):
        """is_activeプロパティ（True）のテスト"""
        group = Group(name="testgroup")

        assert group.is_active is True
        assert group.is_deleted is False

    def test_is_active_property_false(self):
        """is_activeプロパティ（False）のテスト"""
        group = Group(name="testgroup", deleted_at=datetime.now(timezone.utc))

        assert group.is_active is False
        assert group.is_deleted is True

    def test_soft_delete(self):
        """論理削除のテスト"""
        group = Group(name="testgroup")

        # 削除前の確認
        assert group.is_active is True
        assert group.deleted_at is None

        # 論理削除実行
        group.soft_delete()

        # 削除後の確認
        assert group.is_active is False
        assert group.deleted_at is not None
        assert isinstance(group.deleted_at, datetime)

    def test_repr_active_group(self):
        """__repr__メソッド（アクティブグループ）のテスト"""
        group = Group(id=1, name="testgroup")

        repr_str = repr(group)
        assert "Group(id=1" in repr_str
        assert "name='testgroup'" in repr_str
        assert "status='active'" in repr_str

    def test_repr_deleted_group(self):
        """__repr__メソッド（削除済みグループ）のテスト"""
        group = Group(id=1, name="testgroup", deleted_at=datetime.now(timezone.utc))

        repr_str = repr(group)
        assert "Group(id=1" in repr_str
        assert "name='testgroup'" in repr_str
        assert "status='deleted'" in repr_str


class TestMembershipModel:
    """Membershipモデルのテストクラス"""

    def test_membership_creation(self):
        """メンバーシップ作成のテスト"""
        membership = Membership(user_id=1, group_id=1)

        assert membership.user_id == 1
        assert membership.group_id == 1
        assert membership.deleted_at is None

    def test_is_active_property_true(self):
        """is_activeプロパティ（True）のテスト"""
        membership = Membership(user_id=1, group_id=1)

        assert membership.is_active is True
        assert membership.is_deleted is False

    def test_is_active_property_false(self):
        """is_activeプロパティ（False）のテスト"""
        membership = Membership(
            user_id=1, group_id=1, deleted_at=datetime.now(timezone.utc)
        )

        assert membership.is_active is False
        assert membership.is_deleted is True

    def test_soft_delete(self):
        """論理削除のテスト"""
        membership = Membership(user_id=1, group_id=1)

        # 削除前の確認
        assert membership.is_active is True
        assert membership.deleted_at is None

        # 論理削除実行
        membership.soft_delete()

        # 削除後の確認
        assert membership.is_active is False
        assert membership.deleted_at is not None
        assert isinstance(membership.deleted_at, datetime)

    def test_repr_active_membership(self):
        """__repr__メソッド（アクティブメンバーシップ）のテスト"""
        membership = Membership(id=1, user_id=2, group_id=3)

        repr_str = repr(membership)
        assert "Membership(id=1" in repr_str
        assert "user_id=2" in repr_str
        assert "group_id=3" in repr_str
        assert "status='active'" in repr_str

    def test_repr_deleted_membership(self):
        """__repr__メソッド（削除済みメンバーシップ）のテスト"""
        membership = Membership(
            id=1, user_id=2, group_id=3, deleted_at=datetime.now(timezone.utc)
        )

        repr_str = repr(membership)
        assert "Membership(id=1" in repr_str
        assert "user_id=2" in repr_str
        assert "group_id=3" in repr_str
        assert "status='deleted'" in repr_str
