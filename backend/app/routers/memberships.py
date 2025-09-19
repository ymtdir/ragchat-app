"""メンバーシップAPI

メンバーシップに関するAPIエンドポイントを提供します。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..services.memberships import MembershipService
from ..schemas.memberships import (
    MembershipCreate,
    MembershipResponse,
    MembersResponse,
    UserMembershipsResponse,
    BulkMembershipCreate,
    BulkMembershipResponse,
    BulkMembershipDelete,
    BulkMembershipDeleteResponse,
    MemberDeleteResponse,
)

router = APIRouter(prefix="/api/memberships", tags=["memberships"])


@router.post(
    "/",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="グループメンバーを追加",
    description="指定されたグループに指定されたユーザーを追加します。",
)
async def add_member_to_group(
    membership: MembershipCreate, db: Session = Depends(get_db)
):
    """グループにメンバーを追加する"""
    try:
        result = MembershipService.add_member_to_group(
            db, membership.group_id, membership.user_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"メンバー追加処理中にエラーが発生しました: {str(e)}",
        )


@router.delete(
    "/groups/{group_id}/users/{user_id}",
    response_model=MemberDeleteResponse,
    summary="グループメンバーを削除",
    description="指定されたグループから指定されたユーザーを削除します。",
)
async def remove_member_from_group(
    group_id: int, user_id: int, db: Session = Depends(get_db)
):
    """グループからメンバーを削除する"""
    try:
        success = MembershipService.remove_member_from_group(db, group_id, user_id)
        if success:
            return MemberDeleteResponse(
                message="メンバーが正常に削除されました", deleted_count=1
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="指定されたメンバーシップが見つかりません",
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"メンバー削除処理中にエラーが発生しました: {str(e)}",
        )


@router.get(
    "/groups/{group_id}/members",
    response_model=MembersResponse,
    summary="グループメンバー一覧を取得",
    description="指定されたグループのメンバー一覧を取得します。",
)
async def get_group_members(
    group_id: int, include_deleted: bool = False, db: Session = Depends(get_db)
):
    """グループのメンバー一覧を取得する"""
    try:
        members = MembershipService.get_group_members(db, group_id, include_deleted)
        return MembersResponse(
            group_id=group_id, members=members, total_count=len(members)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"グループメンバー取得処理中にエラーが発生しました: {str(e)}",
        )


@router.get(
    "/users/{user_id}/groups",
    response_model=UserMembershipsResponse,
    summary="ユーザーの所属グループ一覧を取得",
    description="指定されたユーザーが所属するグループの一覧を取得します。",
)
async def get_user_groups(
    user_id: int, include_deleted: bool = False, db: Session = Depends(get_db)
):
    """ユーザーの所属グループ一覧を取得する"""
    try:
        groups = MembershipService.get_user_groups(db, user_id, include_deleted)
        return UserMembershipsResponse(
            user_id=user_id, groups=groups, total_count=len(groups)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ユーザーグループ取得処理中にエラーが発生しました: {str(e)}",
        )


@router.post(
    "/bulk-add",
    response_model=BulkMembershipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="複数メンバーを一括追加",
    description="指定されたグループに複数のユーザーを一括で追加します。",
)
async def add_multiple_members_to_group(
    bulk_membership: BulkMembershipCreate, db: Session = Depends(get_db)
):
    """グループに複数のメンバーを一括追加する"""
    try:
        result = MembershipService.add_multiple_members_to_group(
            db, bulk_membership.group_id, bulk_membership.user_ids
        )

        return BulkMembershipResponse(
            message="一括メンバー追加処理が完了しました",
            group_id=bulk_membership.group_id,
            added_count=result["added_count"],
            already_member_count=result["already_member_count"],
            errors=result["errors"],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"一括メンバー追加処理中にエラーが発生しました: {str(e)}",
        )


@router.post(
    "/bulk-remove",
    response_model=BulkMembershipDeleteResponse,
    summary="複数メンバーを一括削除",
    description="指定されたグループから複数のユーザーを一括で削除します。",
)
async def remove_multiple_members_from_group(
    bulk_membership: BulkMembershipDelete, db: Session = Depends(get_db)
):
    """グループから複数のメンバーを一括削除する"""
    try:
        result = MembershipService.remove_multiple_members_from_group(
            db, bulk_membership.group_id, bulk_membership.user_ids
        )

        return BulkMembershipDeleteResponse(
            message="一括メンバー削除処理が完了しました",
            group_id=bulk_membership.group_id,
            removed_count=result["removed_count"],
            not_member_count=result["not_member_count"],
            errors=result["errors"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"一括メンバー削除処理中にエラーが発生しました: {str(e)}",
        )


@router.get(
    "/users/{user_id}/groups/{group_id}/membership",
    response_model=dict,
    summary="メンバーシップ確認",
    description="指定されたユーザーが指定されたグループのメンバーかどうかを確認します。",
)
async def check_membership(user_id: int, group_id: int, db: Session = Depends(get_db)):
    """ユーザーがグループのメンバーかどうかを確認する"""
    try:
        is_member = MembershipService.is_member_of_group(db, user_id, group_id)
        return {"user_id": user_id, "group_id": group_id, "is_member": is_member}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"メンバーシップ確認処理中にエラーが発生しました: {str(e)}",
        )
