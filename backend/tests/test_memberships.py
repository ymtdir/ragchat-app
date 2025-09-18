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

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.group import Group
from app.models.membership import Membership


class TestMemberships:
    """メンバーシップAPIのテストクラス"""

    def setup_method(self):
        """各テストメソッド実行前の準備"""
        pass

    def test_add_member_to_group_success(self, client: TestClient, db: Session):
        """グループメンバー追加 - 成功"""
        # テストユーザーとグループを作成
        user = User(name="testuser", email="test@example.com", password="hashedpass")
        group = Group(name="testgroup", description="Test Group")
        db.add_all([user, group])
        db.commit()
        db.refresh(user)
        db.refresh(group)

        # メンバー追加
        response = client.post(
            "/api/memberships/", json={"user_id": user.id, "group_id": group.id}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == user.id
        assert data["group_id"] == group.id
        assert "created_at" in data

    def test_add_member_to_group_user_not_found(self, client: TestClient, db: Session):
        """グループメンバー追加 - ユーザーが存在しない"""
        # テストグループのみ作成
        group = Group(name="testgroup", description="Test Group")
        db.add(group)
        db.commit()
        db.refresh(group)

        # 存在しないユーザーでメンバー追加
        response = client.post(
            "/api/memberships/", json={"user_id": 999, "group_id": group.id}
        )

        assert response.status_code == 400
        assert "ユーザーが見つかりません" in response.json()["detail"]

    def test_add_member_to_group_group_not_found(self, client: TestClient, db: Session):
        """グループメンバー追加 - グループが存在しない"""
        # テストユーザーのみ作成
        user = User(name="testuser", email="test@example.com", password="hashedpass")
        db.add(user)
        db.commit()
        db.refresh(user)

        # 存在しないグループでメンバー追加
        response = client.post(
            "/api/memberships/", json={"user_id": user.id, "group_id": 999}
        )

        assert response.status_code == 400
        assert "グループが見つかりません" in response.json()["detail"]

    def test_add_member_to_group_already_member(self, client: TestClient, db: Session):
        """グループメンバー追加 - 既にメンバー"""
        # テストユーザーとグループを作成
        user = User(name="testuser", email="test@example.com", password="hashedpass")
        group = Group(name="testgroup", description="Test Group")
        db.add_all([user, group])
        db.commit()
        db.refresh(user)
        db.refresh(group)

        # 既にメンバーシップを作成
        membership = Membership(user_id=user.id, group_id=group.id)
        db.add(membership)
        db.commit()

        # 重複してメンバー追加
        response = client.post(
            "/api/memberships/", json={"user_id": user.id, "group_id": group.id}
        )

        assert response.status_code == 400
        assert "既にこのグループのメンバーです" in response.json()["detail"]

    def test_remove_member_from_group_success(self, client: TestClient, db: Session):
        """グループメンバー削除 - 成功"""
        # テストユーザー、グループ、メンバーシップを作成
        user = User(name="testuser", email="test@example.com", password="hashedpass")
        group = Group(name="testgroup", description="Test Group")
        db.add_all([user, group])
        db.commit()
        db.refresh(user)
        db.refresh(group)

        membership = Membership(user_id=user.id, group_id=group.id)
        db.add(membership)
        db.commit()

        # メンバー削除
        response = client.delete(f"/api/memberships/groups/{group.id}/users/{user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "メンバーが正常に削除されました"
        assert data["deleted_count"] == 1

    def test_remove_member_from_group_not_member(self, client: TestClient, db: Session):
        """グループメンバー削除 - メンバーでない"""
        # テストユーザーとグループを作成（メンバーシップは作成しない）
        user = User(name="testuser", email="test@example.com", password="hashedpass")
        group = Group(name="testgroup", description="Test Group")
        db.add_all([user, group])
        db.commit()
        db.refresh(user)
        db.refresh(group)

        # メンバーでないユーザーの削除
        response = client.delete(f"/api/memberships/groups/{group.id}/users/{user.id}")

        assert response.status_code == 404
        assert "指定されたメンバーシップが見つかりません" in response.json()["detail"]

    def test_get_group_members(self, client: TestClient, db: Session):
        """グループメンバー一覧取得"""
        # テストデータ作成
        users = [
            User(name=f"user{i}", email=f"user{i}@example.com", password="hashedpass")
            for i in range(1, 4)
        ]
        group = Group(name="testgroup", description="Test Group")

        db.add_all(users + [group])
        db.commit()

        # メンバーシップ作成
        for user in users:
            db.refresh(user)
            membership = Membership(user_id=user.id, group_id=group.id)
            db.add(membership)
        db.commit()
        db.refresh(group)

        # メンバー一覧取得
        response = client.get(f"/api/memberships/groups/{group.id}/members")

        assert response.status_code == 200
        data = response.json()
        assert data["group_id"] == group.id
        assert data["total_count"] == 3
        assert len(data["members"]) == 3

        # メンバー情報の確認
        member_names = [member["user_name"] for member in data["members"]]
        assert "user1" in member_names
        assert "user2" in member_names
        assert "user3" in member_names

    def test_get_user_groups(self, client: TestClient, db: Session):
        """ユーザーの所属グループ一覧取得"""
        # テストデータ作成
        user = User(name="testuser", email="test@example.com", password="hashedpass")
        groups = [
            Group(name=f"group{i}", description=f"Test Group {i}") for i in range(1, 4)
        ]

        db.add_all([user] + groups)
        db.commit()
        db.refresh(user)

        # メンバーシップ作成
        for group in groups:
            db.refresh(group)
            membership = Membership(user_id=user.id, group_id=group.id)
            db.add(membership)
        db.commit()

        # 所属グループ一覧取得
        response = client.get(f"/api/memberships/users/{user.id}/groups")

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user.id
        assert data["total_count"] == 3
        assert len(data["groups"]) == 3

        # グループ情報の確認
        group_names = [group["group_name"] for group in data["groups"]]
        assert "group1" in group_names
        assert "group2" in group_names
        assert "group3" in group_names

    def test_bulk_add_members(self, client: TestClient, db: Session):
        """複数メンバー一括追加"""
        # テストデータ作成
        users = [
            User(name=f"user{i}", email=f"user{i}@example.com", password="hashedpass")
            for i in range(1, 4)
        ]
        group = Group(name="testgroup", description="Test Group")

        db.add_all(users + [group])
        db.commit()

        user_ids = [user.id for user in users]
        db.refresh(group)

        # 一括メンバー追加
        response = client.post(
            "/api/memberships/bulk-add",
            json={"group_id": group.id, "user_ids": user_ids},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["group_id"] == group.id
        assert data["added_count"] == 3
        assert data["already_member_count"] == 0
        assert len(data["errors"]) == 0

    def test_bulk_add_members_with_existing(self, client: TestClient, db: Session):
        """複数メンバー一括追加 - 一部が既にメンバー"""
        # テストデータ作成
        users = [
            User(name=f"user{i}", email=f"user{i}@example.com", password="hashedpass")
            for i in range(1, 4)
        ]
        group = Group(name="testgroup", description="Test Group")

        db.add_all(users + [group])
        db.commit()

        # 1人目を既にメンバーとして追加
        db.refresh(users[0])
        db.refresh(group)
        existing_membership = Membership(user_id=users[0].id, group_id=group.id)
        db.add(existing_membership)
        db.commit()

        user_ids = [user.id for user in users]

        # 一括メンバー追加
        response = client.post(
            "/api/memberships/bulk-add",
            json={"group_id": group.id, "user_ids": user_ids},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["group_id"] == group.id
        assert data["added_count"] == 2  # 新規追加は2人
        assert data["already_member_count"] == 1  # 1人は既にメンバー
        assert len(data["errors"]) == 0

    def test_bulk_remove_members(self, client: TestClient, db: Session):
        """複数メンバー一括削除"""
        # テストデータ作成
        users = [
            User(name=f"user{i}", email=f"user{i}@example.com", password="hashedpass")
            for i in range(1, 4)
        ]
        group = Group(name="testgroup", description="Test Group")

        db.add_all(users + [group])
        db.commit()

        # メンバーシップ作成
        for user in users:
            db.refresh(user)
            membership = Membership(user_id=user.id, group_id=group.id)
            db.add(membership)
        db.commit()
        db.refresh(group)

        user_ids = [user.id for user in users]

        # 一括メンバー削除
        response = client.post(
            "/api/memberships/bulk-remove",
            json={"group_id": group.id, "user_ids": user_ids},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["group_id"] == group.id
        assert data["removed_count"] == 3
        assert data["not_member_count"] == 0
        assert len(data["errors"]) == 0

    def test_check_membership_true(self, client: TestClient, db: Session):
        """メンバーシップ確認 - メンバーの場合"""
        # テストユーザー、グループ、メンバーシップを作成
        user = User(name="testuser", email="test@example.com", password="hashedpass")
        group = Group(name="testgroup", description="Test Group")
        db.add_all([user, group])
        db.commit()
        db.refresh(user)
        db.refresh(group)

        membership = Membership(user_id=user.id, group_id=group.id)
        db.add(membership)
        db.commit()

        # メンバーシップ確認
        response = client.get(
            f"/api/memberships/users/{user.id}/groups/{group.id}/membership"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user.id
        assert data["group_id"] == group.id
        assert data["is_member"] is True

    def test_check_membership_false(self, client: TestClient, db: Session):
        """メンバーシップ確認 - メンバーでない場合"""
        # テストユーザーとグループを作成（メンバーシップは作成しない）
        user = User(name="testuser", email="test@example.com", password="hashedpass")
        group = Group(name="testgroup", description="Test Group")
        db.add_all([user, group])
        db.commit()
        db.refresh(user)
        db.refresh(group)

        # メンバーシップ確認
        response = client.get(
            f"/api/memberships/users/{user.id}/groups/{group.id}/membership"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user.id
        assert data["group_id"] == group.id
        assert data["is_member"] is False
