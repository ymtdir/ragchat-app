"""メンバーシップスキーマ

メンバーシップ関連のPydanticスキーマを定義します。
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class MembershipBase(BaseModel):
    """メンバーシップベーススキーマ"""

    user_id: int = Field(..., description="ユーザーID")
    group_id: int = Field(..., description="グループID")


class MembershipCreate(MembershipBase):
    """メンバーシップ作成用スキーマ

    Examples:
        {
            "user_id": 1,
            "group_id": 2
        }
    """
    pass


class MembershipResponse(MembershipBase):
    """メンバーシップレスポンス用スキーマ"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="メンバーシップID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    deleted_at: Optional[datetime] = Field(None, description="削除日時")


class MembershipWithUser(MembershipResponse):
    """ユーザー情報付きメンバーシップレスポンス用スキーマ"""

    user: dict = Field(..., description="ユーザー情報")


class MembershipWithGroup(MembershipResponse):
    """グループ情報付きメンバーシップレスポンス用スキーマ"""

    group: dict = Field(..., description="グループ情報")


class MembershipUpdate(BaseModel):
    """メンバーシップ更新用スキーマ

    現在は特に更新可能なフィールドがありませんが、将来の拡張のために定義
    """
    pass


class MemberDeleteResponse(BaseModel):
    """メンバー削除レスポンス用スキーマ"""

    message: str = Field(..., description="削除完了メッセージ")
    deleted_count: int = Field(..., description="削除されたメンバー数")


class MembersResponse(BaseModel):
    """メンバー一覧レスポンス用スキーマ"""

    group_id: int = Field(..., description="グループID")
    members: List[dict] = Field(default=[], description="メンバー一覧")
    total_count: int = Field(..., description="総メンバー数")


class UserMembershipsResponse(BaseModel):
    """ユーザーのメンバーシップ一覧レスポンス用スキーマ"""

    user_id: int = Field(..., description="ユーザーID")
    groups: List[dict] = Field(default=[], description="所属グループ一覧")
    total_count: int = Field(..., description="総所属グループ数")


class BulkMembershipCreate(BaseModel):
    """一括メンバーシップ作成用スキーマ"""

    group_id: int = Field(..., description="グループID")
    user_ids: List[int] = Field(..., description="追加するユーザーIDのリスト", min_length=1)


class BulkMembershipResponse(BaseModel):
    """一括メンバーシップ作成レスポンス用スキーマ"""

    message: str = Field(..., description="処理完了メッセージ")
    group_id: int = Field(..., description="グループID")
    added_count: int = Field(..., description="追加されたメンバー数")
    already_member_count: int = Field(..., description="既にメンバーだった数")
    errors: List[str] = Field(default=[], description="エラーメッセージ")


class BulkMembershipDelete(BaseModel):
    """一括メンバーシップ削除用スキーマ"""

    group_id: int = Field(..., description="グループID")
    user_ids: List[int] = Field(..., description="削除するユーザーIDのリスト", min_length=1)


class BulkMembershipDeleteResponse(BaseModel):
    """一括メンバーシップ削除レスポンス用スキーマ"""

    message: str = Field(..., description="処理完了メッセージ")
    group_id: int = Field(..., description="グループID")
    removed_count: int = Field(..., description="削除されたメンバー数")
    not_member_count: int = Field(..., description="メンバーでなかった数")
    errors: List[str] = Field(default=[], description="エラーメッセージ")