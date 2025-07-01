"""ユーザー関連のAPIエンドポイント

PostgreSQLを使用したユーザー管理のためのREST APIエンドポイントです。
ユーザー情報、認証情報などの構造化データを管理します。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..config.database import get_db
from ..schemas.users import UserCreate, UserResponse
from ..services.users import UserService

# ユーザー管理用ルーター
router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ユーザー登録",
    description="新しいユーザーを登録します。パスワードは自動的にハッシュ化されます。",
    response_description="作成されたユーザー情報",
)
async def create_user(
    user_data: UserCreate,  # リクエストボディ（Pydanticで自動バリデーション）
    db: Session = Depends(get_db),  # データベースセッション（依存性注入）
) -> UserResponse:
    """ユーザーを作成する

    Args:
        user_data: ユーザー作成データ（自動的にバリデーション済み）
        db: データベースセッション（依存性注入）

    Returns:
        UserResponse: 作成されたユーザー情報

    Raises:
        HTTPException: ユーザー名またはメールアドレスが重複している場合（400）
    """

    # 1. ユーザー名の重複チェック
    if UserService.is_name_taken(db, user_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ユーザー名 '{user_data.name}' は既に使用されています",
        )

    # 2. メールアドレスの重複チェック
    if UserService.is_email_taken(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"メールアドレス '{user_data.email}' は既に使用されています",
        )

    # 3. ユーザー作成
    try:
        db_user = UserService.create_user(db, user_data)
        return UserResponse.model_validate(db_user)
    except IntegrityError:
        # データベースレベルでの制約違反（念のため）
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ユーザー名またはメールアドレスが既に使用されています",
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="ユーザー取得",
    description="指定されたIDのユーザー情報を取得します。",
    response_description="ユーザー情報",
)
async def get_user(
    user_id: int,  # パスパラメータ
    db: Session = Depends(get_db),  # データベースセッション（依存性注入）
) -> UserResponse:
    """ユーザー情報を取得する

    Args:
        user_id: ユーザーID
        db: データベースセッション（依存性注入）

    Returns:
        UserResponse: ユーザー情報

    Raises:
        HTTPException: ユーザーが存在しない場合（404）
    """

    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {user_id} のユーザーが見つかりません",
        )

    return UserResponse.model_validate(user)
