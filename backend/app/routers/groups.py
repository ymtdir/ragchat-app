"""グループ関連のAPIエンドポイント

PostgreSQLを使用したグループ管理のためのREST APIエンドポイントです。
グループ情報などの構造化データを管理します。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..config.database import get_db
from ..schemas.groups import (
    GroupCreate,
    GroupResponse,
    GroupsResponse,
    GroupUpdate,
    GroupDeleteResponse,
)
from ..services.groups import GroupService

# グループ管理用ルーター
router = APIRouter(
    prefix="/api/groups",
    tags=["groups"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="グループ作成",
    description="新しいグループを作成します。",
    response_description="作成されたグループ情報",
)
async def create_group(
    group_data: GroupCreate,  # リクエストボディ（Pydanticで自動バリデーション）
    db: Session = Depends(get_db),  # データベースセッション（依存性注入）
) -> GroupResponse:
    """グループを作成する

    Args:
        group_data: グループ作成データ（自動的にバリデーション済み）
        db: データベースセッション（依存性注入）

    Returns:
        GroupResponse: 作成されたグループ情報

    Raises:
        HTTPException: グループ名が重複している場合（400）
    """

    # グループ名の重複チェック
    if GroupService.is_name_taken(db, group_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"グループ名 '{group_data.name}' は既に使用されています",
        )

    # グループ作成
    try:
        db_group = GroupService.create_group(db, group_data)
        return GroupResponse.model_validate(db_group)
    except IntegrityError:
        # データベースレベルでの制約違反（グループ名の重複のみ）
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="グループ名が既に使用されています",
        )


@router.get(
    "/",
    response_model=GroupsResponse,
    summary="全グループ取得",
    description="登録されている全グループの情報を取得します。",
    response_description="全グループ情報と総数",
)
async def get_all_groups(
    db: Session = Depends(get_db),  # データベースセッション（依存性注入）
) -> GroupsResponse:
    """全グループ情報を取得する

    Args:
        db: データベースセッション（依存性注入）

    Returns:
        GroupsResponse: 全グループ情報と総数
    """

    groups = GroupService.get_all_groups(db)
    group_responses = [GroupResponse.model_validate(group) for group in groups]

    return GroupsResponse(groups=group_responses, total=len(group_responses))


@router.get(
    "/{group_id}",
    response_model=GroupResponse,
    summary="グループ取得",
    description="指定されたIDのグループ情報を取得します。",
    response_description="グループ情報",
)
async def get_group(
    group_id: int,  # パスパラメータ
    db: Session = Depends(get_db),  # データベースセッション（依存性注入）
) -> GroupResponse:
    """グループ情報を取得する

    Args:
        group_id: グループID
        db: データベースセッション（依存性注入）

    Returns:
        GroupResponse: グループ情報

    Raises:
        HTTPException: グループが存在しない場合（404）
    """

    group = GroupService.get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {group_id} のグループが見つかりません",
        )

    return GroupResponse.model_validate(group)


@router.put(
    "/{group_id}",
    response_model=GroupResponse,
    summary="グループ更新",
    description="指定されたIDのグループ情報を更新します。名前と説明を更新可能です。",
    response_description="更新されたグループ情報",
)
async def update_group(
    group_id: int,  # パスパラメータ
    group_data: GroupUpdate,  # リクエストボディ
    db: Session = Depends(get_db),  # データベースセッション（依存性注入）
) -> GroupResponse:
    """グループ情報を更新する

    Args:
        group_id: グループID
        group_data: 更新データ（自動的にバリデーション済み）
        db: データベースセッション（依存性注入）

    Returns:
        GroupResponse: 更新されたグループ情報

    Raises:
        HTTPException: グループが存在しない場合（404）
        HTTPException: グループ名が重複している場合（400）
    """

    try:
        updated_group = GroupService.update_group(db, group_id, group_data)
        if not updated_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID {group_id} のグループが見つかりません",
            )

        return GroupResponse.model_validate(updated_group)

    except IntegrityError:
        # データベース制約違反（グループ名の重複のみ）
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="グループ名が既に使用されています",
        )


@router.delete(
    "/{group_id}",
    response_model=GroupDeleteResponse,
    summary="グループ削除",
    description="指定されたIDのグループを削除します。",
    response_description="削除結果",
)
async def delete_group(
    group_id: int,  # パスパラメータ
    db: Session = Depends(get_db),  # データベースセッション（依存性注入）
) -> GroupDeleteResponse:
    """指定されたIDのグループを削除する

    Args:
        group_id: 削除対象のグループID
        db: データベースセッション（依存性注入）

    Returns:
        GroupDeleteResponse: 削除結果

    Raises:
        HTTPException: グループが存在しない場合（404）
        HTTPException: 削除処理中にエラーが発生した場合（500）
    """

    try:
        success = GroupService.delete_group_by_id(db, group_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID {group_id} のグループが見つかりません",
            )

        return GroupDeleteResponse(
            message="グループが正常に削除されました",
            deleted_count=1,
        )

    except HTTPException:
        # HTTPExceptionは再キャッチしない
        raise
    except Exception as e:
        print(f"Delete endpoint error: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"グループ削除中にエラーが発生しました: {str(e)}",
        )


@router.delete(
    "/",
    response_model=GroupDeleteResponse,
    summary="全グループ削除",
    description="登録されている全グループを削除します。この操作は取り消すことができません。",
    response_description="削除結果",
)
async def delete_all_groups(
    db: Session = Depends(get_db),  # データベースセッション（依存性注入）
) -> GroupDeleteResponse:
    """全グループを削除する

    Args:
        db: データベースセッション（依存性注入）

    Returns:
        GroupDeleteResponse: 削除結果

    Raises:
        HTTPException: 削除処理中にエラーが発生した場合（500）
    """

    try:
        deleted_count = GroupService.delete_all_groups(db)

        return GroupDeleteResponse(
            message=f"{deleted_count}個のグループが正常に削除されました",
            deleted_count=deleted_count,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"全グループ削除中にエラーが発生しました: {str(e)}",
        )
