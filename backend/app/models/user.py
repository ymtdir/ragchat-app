"""ユーザーモデル

ユーザー情報を管理するSQLAlchemyモデルです。
"""

from sqlalchemy import Column, Integer, String
from ..config.database import Base


class User(Base):
    """ユーザーモデルクラス

    Attributes:
        id: プライマリキー
        name: ユーザー名（ユニーク）
        email: メールアドレス（ユニーク）
        password: パスワード（ハッシュ化済み）
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)

    def __repr__(self):
        """文字列表現を返す

        Returns:
            str: ユーザーの文字列表現
        """
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
