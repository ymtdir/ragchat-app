"""ユーザーモデル

ユーザー情報を管理するSQLAlchemyモデルです。
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..config.database import Base


class User(Base):
    """ユーザーモデルクラス

    Attributes:
        id: プライマリキー
        name: ユーザー名（ユニーク）
        email: メールアドレス（ユニーク）
        password: パスワード（ハッシュ化済み）
        created_at: 作成日時
        updated_at: 更新日時
        deleted_at: 削除日時（論理削除用、NULLの場合は有効）
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, nullable=False)
    email = Column(String(100), index=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at = Column(DateTime, nullable=True, index=True)

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
            str: ユーザーの文字列表現
        """
        status = "deleted" if self.is_deleted else "active"
        return (
            f"<User(id={self.id}, name='{self.name}', "
            f"email='{self.email}', status='{status}')>"
        )
