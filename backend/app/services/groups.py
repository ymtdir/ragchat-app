"""グループサービス

グループ関連のビジネスロジックを処理します。
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models.group import Group
from ..schemas.groups import GroupCreate, GroupUpdate


class GroupService:
    """グループサービスクラス

    データベース操作とビジネスルールの実装を担当。
    """

    @staticmethod
    def create_group(db: Session, group_data: GroupCreate) -> Group:
        """グループを作成する

        Args:
            db: データベースセッション
            group_data: グループ作成データ

        Returns:
            Group: 作成されたグループオブジェクト

        Raises:
            IntegrityError: グループ名が重複している場合
        """
        # SQLAlchemyモデルインスタンスの作成
        db_group = Group(name=group_data.name, description=group_data.description)

        try:
            # データベースに追加
            db.add(db_group)
            db.commit()
            db.refresh(db_group)  # 自動生成されたIDなどを取得
            return db_group
        except IntegrityError as e:
            db.rollback()
            # グループ名の重複エラーの場合のみ再発生
            if "name" in str(e).lower():
                raise IntegrityError("グループ名が既に使用されています", None, None)
            # その他のIntegrityErrorは再発生
            raise

    @staticmethod
    def get_group_by_id(
        db: Session, group_id: int, include_deleted: bool = False
    ) -> Optional[Group]:
        """IDでグループを取得する

        Args:
            db: データベースセッション
            group_id: グループID
            include_deleted: 削除済みグループも含めるかどうか

        Returns:
            Optional[Group]: グループオブジェクト（存在しない場合はNone）
        """
        query = db.query(Group).filter(Group.id == group_id)
        if not include_deleted:
            query = query.filter(Group.deleted_at.is_(None))
        return query.first()

    @staticmethod
    def get_group_by_name(
        db: Session, name: str, include_deleted: bool = False
    ) -> Optional[Group]:
        """グループ名でグループを取得する

        Args:
            db: データベースセッション
            name: グループ名
            include_deleted: 削除済みグループも含めるかどうか

        Returns:
            Optional[Group]: グループオブジェクト（存在しない場合はNone）
        """
        query = db.query(Group).filter(Group.name == name)
        if not include_deleted:
            query = query.filter(Group.deleted_at.is_(None))
        return query.first()

    @staticmethod
    def get_all_groups(db: Session, include_deleted: bool = False) -> list[Group]:
        """全グループを取得する

        Args:
            db: データベースセッション
            include_deleted: 削除済みグループも含めるかどうか

        Returns:
            list[Group]: グループのリスト（論理削除されていないもの）
        """
        query = db.query(Group)
        if not include_deleted:
            query = query.filter(Group.deleted_at.is_(None))
        return query.all()

    @staticmethod
    def is_name_taken(db: Session, name: str) -> bool:
        """グループ名が既に使用されているかチェックする

        Args:
            db: データベースセッション
            name: チェックするグループ名

        Returns:
            bool: 使用済みの場合True、利用可能な場合False
        """
        return GroupService.get_group_by_name(db, name) is not None

    @staticmethod
    def update_group(
        db: Session, group_id: int, group_data: GroupUpdate
    ) -> Optional[Group]:
        """グループ情報を更新する

        Args:
            db: データベースセッション
            group_id: 更新対象のグループID
            group_data: 更新データ

        Returns:
            Optional[Group]: 更新されたグループオブジェクト（存在しない場合はNone）

        Raises:
            IntegrityError: グループ名が重複している場合
        """
        # グループの存在確認
        group = GroupService.get_group_by_id(db, group_id)
        if not group:
            return None

        # グループ名の更新（重複チェック付き）
        if group_data.name is not None and group_data.name != group.name:
            if GroupService.is_name_taken(db, group_data.name):
                raise IntegrityError("グループ名が既に使用されています", None, None)
            group.name = group_data.name

        # 説明の更新
        if group_data.description is not None:
            group.description = group_data.description

        try:
            db.commit()
            db.refresh(group)
            return group
        except IntegrityError as e:
            db.rollback()
            # グループ名の重複エラーの場合のみ再発生
            if "name" in str(e).lower():
                raise IntegrityError("グループ名が既に使用されています", None, None)
            # その他のIntegrityErrorは再発生
            raise

    @staticmethod
    def soft_delete_group_by_id(db: Session, group_id: int) -> bool:
        """指定されたIDのグループを論理削除する

        Args:
            db: データベースセッション
            group_id: 削除対象のグループID

        Returns:
            bool: 削除成功の場合True、グループが存在しない場合False
        """
        group = GroupService.get_group_by_id(db, group_id, include_deleted=False)
        if not group:
            return False

        try:
            group.soft_delete()
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def hard_delete_group_by_id(db: Session, group_id: int) -> bool:
        """指定されたIDのグループを物理削除する

        Args:
            db: データベースセッション
            group_id: 削除対象のグループID

        Returns:
            bool: 削除成功の場合True、グループが存在しない場合False
        """
        group = GroupService.get_group_by_id(db, group_id, include_deleted=True)
        if not group:
            return False

        try:
            db.delete(group)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def restore_group_by_id(db: Session, group_id: int) -> bool:
        """指定されたIDのグループを復元する

        Args:
            db: データベースセッション
            group_id: 復元対象のグループID

        Returns:
            bool: 復元成功の場合True、グループが存在しない場合False
        """
        group = GroupService.get_group_by_id(db, group_id, include_deleted=True)
        if not group or not group.is_deleted:
            return False

        try:
            group.deleted_at = None
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def soft_delete_all_groups(db: Session) -> int:
        """全グループを論理削除する

        Args:
            db: データベースセッション

        Returns:
            int: 削除されたグループ数

        Raises:
            Exception: 削除処理中にエラーが発生した場合
        """
        try:
            # アクティブな全グループを取得して論理削除
            groups = GroupService.get_all_groups(db, include_deleted=False)
            deleted_count = len(groups)

            for group in groups:
                group.soft_delete()

            db.commit()
            return deleted_count
        except Exception:
            db.rollback()
            raise

    # 下位互換性のためのエイリアス
    @staticmethod
    def delete_group_by_id(db: Session, group_id: int) -> bool:
        """指定されたIDのグループを削除する（論理削除）

        Note: 下位互換性のために残されています。soft_delete_group_by_idの使用を推奨します。
        """
        return GroupService.soft_delete_group_by_id(db, group_id)

    @staticmethod
    def delete_all_groups(db: Session) -> int:
        """全グループを削除する（論理削除）

        Note: 下位互換性のために残されています。soft_delete_all_groupsの使用を推奨します。
        """
        return GroupService.soft_delete_all_groups(db)
