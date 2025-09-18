"""グループ関連のPydanticスキーマ

リクエスト/レスポンスのバリデーションとシリアライゼーションを行います。
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class GroupCreate(BaseModel):
    """グループ作成用スキーマ

    POSTリクエストで受け取るデータの形式を定義します。

    Attributes:
        name: グループ名（必須、1-100文字）
        description: グループの説明（オプション）
    """

    name: str = Field(..., min_length=1, max_length=100, description="グループ名")
    description: Optional[str] = Field(None, description="グループの説明")

    class Config:
        """設定クラス"""

        # JSON Schema用のサンプルデータ
        json_schema_extra = {
            "example": {
                "name": "group",
                "description": "group description",
            }
        }


class GroupResponse(BaseModel):
    """グループレスポンス用スキーマ

    APIレスポンスで返すデータの形式を定義します。

    Attributes:
        id: グループID
        name: グループ名
        description: グループの説明
        created_at: 作成日時
        updated_at: 更新日時
        deleted_at: 削除日時（論理削除用）
    """

    id: int
    name: str
    description: Optional[str] = None
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
                "name": "group",
                "description": "group description",
                "created_at": "2024-01-01T10:00:00Z",
                "updated_at": "2024-01-01T10:00:00Z",
                "deleted_at": None,
            }
        }


class GroupUpdate(BaseModel):
    """グループ更新用スキーマ

    PUTリクエストで受け取るデータの形式を定義します。

    Attributes:
        name: グループ名（オプション、1-100文字）
        description: グループの説明（オプション）
    """

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="グループ名"
    )
    description: Optional[str] = Field(None, description="グループの説明")

    class Config:
        """設定クラス"""

        # JSON Schema用のサンプルデータ
        json_schema_extra = {
            "example": {
                "name": "updated group",
                "description": "updated group description",
            }
        }


class GroupDeleteResponse(BaseModel):
    """グループ削除レスポンス用スキーマ

    APIレスポンスで返す削除結果の形式を定義します。

    Attributes:
        message: 削除完了メッセージ
        deleted_count: 削除されたグループ数
    """

    message: str
    deleted_count: int

    class Config:
        """設定クラス"""

        # JSON Schema用のサンプルデータ
        json_schema_extra = {
            "example": {
                "message": "グループが正常に削除されました",
                "deleted_count": 1,
            }
        }


class GroupsResponse(BaseModel):
    """全グループレスポンス用スキーマ

    APIレスポンスで返す全グループデータの形式を定義します。

    Attributes:
        groups: グループリスト
        total: グループ総数
    """

    groups: list[GroupResponse]
    total: int

    class Config:
        """設定クラス"""

        # JSON Schema用のサンプルデータ
        json_schema_extra = {
            "example": {
                "groups": [
                    {
                        "id": 1,
                        "name": "group01",
                        "description": "group01 description",
                        "created_at": "2024-01-01T10:00:00Z",
                        "updated_at": "2024-01-01T10:00:00Z",
                        "deleted_at": None,
                    },
                    {
                        "id": 2,
                        "name": "group02",
                        "description": "group02 description",
                        "created_at": "2024-01-02T10:00:00Z",
                        "updated_at": "2024-01-02T10:00:00Z",
                        "deleted_at": None,
                    },
                ],
                "total": 2,
            }
        }
