"""ユーザー関連のPydanticスキーマ

リクエスト/レスポンスのバリデーションとシリアライゼーションを行います。
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    """ユーザー作成用スキーマ

    POSTリクエストで受け取るデータの形式を定義します。

    Attributes:
        name: ユーザー名（必須、3-50文字）
        email: メールアドレス（必須、有効なメール形式）
        password: パスワード（必須、8文字以上）
    """

    name: str = Field(..., min_length=3, max_length=50, description="ユーザー名")
    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(..., min_length=8, description="パスワード")

    class Config:
        """設定クラス"""

        # JSON Schema用のサンプルデータ
        json_schema_extra = {
            "example": {
                "name": "user",
                "email": "user@example.com",
                "password": "P@ssw0rd",
            }
        }


class UserResponse(BaseModel):
    """ユーザーレスポンス用スキーマ

    APIレスポンスで返すデータの形式を定義します。
    セキュリティのためパスワードは含めません。

    Attributes:
        id: ユーザーID
        name: ユーザー名
        email: メールアドレス
        created_at: 作成日時
        updated_at: 更新日時
        deleted_at: 削除日時（論理削除用）
    """

    id: int
    name: str
    email: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        """設定クラス"""

        from_attributes = True  # SQLAlchemyモデルからの変換を有効化

        # JSON Schema用のサンプルデータ
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "user",
                "email": "user@example.com",
                "created_at": "2024-01-01T10:00:00Z",
                "updated_at": "2024-01-01T10:00:00Z",
                "deleted_at": None
            }
        }


class UserUpdate(BaseModel):
    """ユーザー更新用スキーマ

    PUTリクエストで受け取るデータの形式を定義します。
    名前・メールアドレスとパスワードの両方を更新可能です。

    Attributes:
        name: ユーザー名（オプション、3-50文字）
        email: メールアドレス（オプション、有効なメール形式）
        current_password: 現在のパスワード（パスワード変更時のみ必須）
        new_password: 新しいパスワード（オプション、8文字以上）
    """

    name: str | None = Field(
        None, min_length=3, max_length=50, description="ユーザー名"
    )
    email: EmailStr | None = Field(None, description="メールアドレス")
    current_password: str | None = Field(None, description="現在のパスワード")
    new_password: str | None = Field(None, min_length=8, description="新しいパスワード")

    class Config:
        """設定クラス"""

        # JSON Schema用のサンプルデータ
        json_schema_extra = {
            "example": {
                "name": "updated_user",
                "email": "updated@example.com",
                "current_password": "oldpassword",
                "new_password": "newpassword123",
            }
        }


class UserDeleteResponse(BaseModel):
    """ユーザー削除レスポンス用スキーマ

    APIレスポンスで返す削除結果の形式を定義します。

    Attributes:
        message: 削除完了メッセージ
        deleted_count: 削除されたユーザー数
    """

    message: str
    deleted_count: int

    class Config:
        """設定クラス"""

        # JSON Schema用のサンプルデータ
        json_schema_extra = {
            "example": {
                "message": "ユーザーが正常に削除されました",
                "deleted_count": 1,
            }
        }


class UsersResponse(BaseModel):
    """全ユーザーレスポンス用スキーマ

    APIレスポンスで返す全ユーザーデータの形式を定義します。
    セキュリティのためパスワードは含めません。

    Attributes:
        users: ユーザーリスト
        total: ユーザー総数
    """

    users: list[UserResponse]
    total: int

    class Config:
        """設定クラス"""

        # JSON Schema用のサンプルデータ
        json_schema_extra = {
            "example": {
                "users": [
                    {
                        "id": 1,
                        "name": "user1",
                        "email": "user1@example.com",
                        "created_at": "2024-01-01T10:00:00Z",
                        "updated_at": "2024-01-01T10:00:00Z",
                        "deleted_at": None
                    },
                    {
                        "id": 2,
                        "name": "user2",
                        "email": "user2@example.com",
                        "created_at": "2024-01-02T10:00:00Z",
                        "updated_at": "2024-01-02T10:00:00Z",
                        "deleted_at": None
                    },
                ],
                "total": 2,
            }
        }
