"""メンバーシップサービス

メンバーシップに関するビジネスロジックを提供します。
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from ..models.membership import Membership
from ..models.user import User
from ..models.group import Group
from ..schemas.memberships import (
    MembershipCreate,
    BulkMembershipCreate,
    BulkMembershipDelete
)


class MembershipService:
    """メンバーシップサービスクラス"""

    @staticmethod
    def add_member_to_group(
        db: Session, group_id: int, user_id: int
    ) -> Membership:
        """グループにメンバーを追加する

        Args:
            db: データベースセッション
            group_id: グループID
            user_id: ユーザーID

        Returns:
            Membership: 作成されたメンバーシップ

        Raises:
            ValueError: グループまたはユーザーが存在しない場合
            IntegrityError: 既にメンバーの場合
        """
        # グループとユーザーの存在確認
        group = db.query(Group).filter(
            and_(Group.id == group_id, Group.deleted_at.is_(None))
        ).first()
        if not group:
            raise ValueError(f"ID {group_id} のグループが見つかりません")

        user = db.query(User).filter(
            and_(User.id == user_id, User.deleted_at.is_(None))
        ).first()
        if not user:
            raise ValueError(f"ID {user_id} のユーザーが見つかりません")

        # 既存メンバーシップの確認
        existing = db.query(Membership).filter(
            and_(
                Membership.user_id == user_id,
                Membership.group_id == group_id,
                Membership.deleted_at.is_(None)
            )
        ).first()

        if existing:
            raise ValueError("ユーザーは既にこのグループのメンバーです")

        # メンバーシップ作成
        membership = Membership(user_id=user_id, group_id=group_id)
        db.add(membership)
        db.commit()
        db.refresh(membership)

        return membership

    @staticmethod
    def remove_member_from_group(
        db: Session, group_id: int, user_id: int
    ) -> bool:
        """グループからメンバーを削除する

        Args:
            db: データベースセッション
            group_id: グループID
            user_id: ユーザーID

        Returns:
            bool: 削除が成功したかどうか

        Raises:
            ValueError: メンバーシップが存在しない場合
        """
        membership = db.query(Membership).filter(
            and_(
                Membership.user_id == user_id,
                Membership.group_id == group_id,
                Membership.deleted_at.is_(None)
            )
        ).first()

        if not membership:
            raise ValueError("指定されたメンバーシップが見つかりません")

        membership.soft_delete()
        db.commit()
        return True

    @staticmethod
    def get_group_members(
        db: Session, group_id: int, include_deleted: bool = False
    ) -> List[Dict[str, Any]]:
        """グループのメンバー一覧を取得する

        Args:
            db: データベースセッション
            group_id: グループID
            include_deleted: 削除されたメンバーも含めるかどうか

        Returns:
            List[Dict[str, Any]]: メンバー一覧
        """
        query = db.query(Membership).join(User).filter(
            Membership.group_id == group_id
        )

        if not include_deleted:
            query = query.filter(Membership.deleted_at.is_(None))

        memberships = query.all()

        members = []
        for membership in memberships:
            member_data = {
                "membership_id": membership.id,
                "user_id": membership.user_id,
                "user_name": membership.user.name,
                "user_email": membership.user.email,
                "joined_at": membership.created_at,
                "is_active": membership.is_active
            }
            members.append(member_data)

        return members

    @staticmethod
    def get_user_groups(
        db: Session, user_id: int, include_deleted: bool = False
    ) -> List[Dict[str, Any]]:
        """ユーザーの所属グループ一覧を取得する

        Args:
            db: データベースセッション
            user_id: ユーザーID
            include_deleted: 削除されたメンバーシップも含めるかどうか

        Returns:
            List[Dict[str, Any]]: 所属グループ一覧
        """
        query = db.query(Membership).join(Group).filter(
            Membership.user_id == user_id
        )

        if not include_deleted:
            query = query.filter(Membership.deleted_at.is_(None))

        memberships = query.all()

        groups = []
        for membership in memberships:
            group_data = {
                "membership_id": membership.id,
                "group_id": membership.group_id,
                "group_name": membership.group.name,
                "group_description": membership.group.description,
                "joined_at": membership.created_at,
                "is_active": membership.is_active
            }
            groups.append(group_data)

        return groups

    @staticmethod
    def add_multiple_members_to_group(
        db: Session, group_id: int, user_ids: List[int]
    ) -> Dict[str, Any]:
        """グループに複数のメンバーを一括追加する

        Args:
            db: データベースセッション
            group_id: グループID
            user_ids: ユーザーIDのリスト

        Returns:
            Dict[str, Any]: 処理結果
        """
        # グループの存在確認
        group = db.query(Group).filter(
            and_(Group.id == group_id, Group.deleted_at.is_(None))
        ).first()
        if not group:
            raise ValueError(f"ID {group_id} のグループが見つかりません")

        added_count = 0
        already_member_count = 0
        errors = []

        for user_id in user_ids:
            try:
                # ユーザーの存在確認
                user = db.query(User).filter(
                    and_(User.id == user_id, User.deleted_at.is_(None))
                ).first()
                if not user:
                    errors.append(f"ID {user_id} のユーザーが見つかりません")
                    continue

                # 既存メンバーシップの確認
                existing = db.query(Membership).filter(
                    and_(
                        Membership.user_id == user_id,
                        Membership.group_id == group_id,
                        Membership.deleted_at.is_(None)
                    )
                ).first()

                if existing:
                    already_member_count += 1
                    continue

                # メンバーシップ作成
                membership = Membership(user_id=user_id, group_id=group_id)
                db.add(membership)
                added_count += 1

            except Exception as e:
                errors.append(f"ユーザー {user_id} の追加に失敗: {str(e)}")

        db.commit()

        return {
            "added_count": added_count,
            "already_member_count": already_member_count,
            "errors": errors
        }

    @staticmethod
    def remove_multiple_members_from_group(
        db: Session, group_id: int, user_ids: List[int]
    ) -> Dict[str, Any]:
        """グループから複数のメンバーを一括削除する

        Args:
            db: データベースセッション
            group_id: グループID
            user_ids: ユーザーIDのリスト

        Returns:
            Dict[str, Any]: 処理結果
        """
        removed_count = 0
        not_member_count = 0
        errors = []

        for user_id in user_ids:
            try:
                membership = db.query(Membership).filter(
                    and_(
                        Membership.user_id == user_id,
                        Membership.group_id == group_id,
                        Membership.deleted_at.is_(None)
                    )
                ).first()

                if not membership:
                    not_member_count += 1
                    continue

                membership.soft_delete()
                removed_count += 1

            except Exception as e:
                errors.append(f"ユーザー {user_id} の削除に失敗: {str(e)}")

        db.commit()

        return {
            "removed_count": removed_count,
            "not_member_count": not_member_count,
            "errors": errors
        }

    @staticmethod
    def is_member_of_group(db: Session, user_id: int, group_id: int) -> bool:
        """ユーザーがグループのメンバーかどうかを確認する

        Args:
            db: データベースセッション
            user_id: ユーザーID
            group_id: グループID

        Returns:
            bool: メンバーの場合True
        """
        membership = db.query(Membership).filter(
            and_(
                Membership.user_id == user_id,
                Membership.group_id == group_id,
                Membership.deleted_at.is_(None)
            )
        ).first()

        return membership is not None