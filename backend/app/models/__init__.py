"""データベースモデル

SQLAlchemyモデルクラスを定義します。
FlaskのModelsに相当する機能を提供。
"""

from .user import User

__all__ = ["User"]
