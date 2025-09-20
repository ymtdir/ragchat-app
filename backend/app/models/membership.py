"""メンバーシップモデル

グループとユーザーの関連を管理するSQLAlchemyモデルです。
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..config.database import Base


class Membership(Base):
    """メンバーシップモデルクラス

    ユーザーとグループの多対多関係を管理します。

    Attributes:
        id: プライマリキー
        user_id: ユーザーID（外部キー）
        group_id: グループID（外部キー）
        created_at: 作成日時（メンバー追加日時）
        updated_at: 更新日時
        deleted_at: 削除日時（論理削除用、NULLの場合は有効なメンバー）
        user: ユーザーオブジェクト（リレーション）
        group: グループオブジェクト（リレーション）
    """

    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at = Column(DateTime, nullable=True, index=True)

    # リレーション
    user = relationship("User", backref="group_memberships")
    group = relationship("Group", backref="user_memberships")

    # ユニーク制約（同じユーザーが同じグループに重複して所属できない）
    __table_args__ = (
        UniqueConstraint(
            "user_id", "group_id", "deleted_at", name="unique_active_membership"
        ),
    )

    @property
    def is_deleted(self) -> bool:
        """削除されているかどうかを確認する

        Returns:
            bool: 削除されている場合はTrue、そうでなければFalse
        """
        return self.deleted_at is not None

    @property
    def is_active(self) -> bool:
        """アクティブかどうかを確認する（削除されていない）

        Returns:
            bool: アクティブ（削除されていない）場合はTrue
        """
        return self.deleted_at is None

    def soft_delete(self):
        """論理削除を実行する"""
        from datetime import datetime, timezone

        self.deleted_at = datetime.now(timezone.utc)

    def __repr__(self):
        """文字列表現を返す

        Returns:
            str: メンバーシップの文字列表現
        """
        status = "deleted" if self.is_deleted else "active"
        return (
            f"<Membership(id={self.id}, user_id={self.user_id}, "
            f"group_id={self.group_id}, status='{status}')>"
        )
