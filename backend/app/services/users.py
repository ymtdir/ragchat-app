"""ユーザーサービス

ユーザー関連のビジネスロジックを処理します。
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from ..models.user import User
from ..schemas.users import UserCreate, UserUpdate

# パスワードハッシュ化用の設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """ユーザーサービスクラス

    データベース操作とビジネスルールの実装を担当。
    """

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """ユーザーを作成する

        Args:
            db: データベースセッション
            user_data: ユーザー作成データ

        Returns:
            User: 作成されたユーザーオブジェクト

        Raises:
            IntegrityError: ユーザー名またはメールアドレスが重複している場合
        """
        # パスワードをハッシュ化
        hashed_password = pwd_context.hash(user_data.password)

        # SQLAlchemyモデルインスタンスの作成
        db_user = User(
            name=user_data.name, email=user_data.email, password=hashed_password
        )

        try:
            # データベースに追加
            db.add(db_user)
            db.commit()
            db.refresh(db_user)  # 自動生成されたIDなどを取得
            return db_user
        except IntegrityError:
            db.rollback()
            raise

    @staticmethod
    def get_user_by_id(db: Session, user_id: int, include_deleted: bool = False) -> Optional[User]:
        """IDでユーザーを取得する

        Args:
            db: データベースセッション
            user_id: ユーザーID
            include_deleted: 削除済みユーザーも含めるかどうか

        Returns:
            Optional[User]: ユーザーオブジェクト（存在しない場合はNone）
        """
        query = db.query(User).filter(User.id == user_id)
        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))
        return query.first()

    @staticmethod
    def get_user_by_name(db: Session, name: str, include_deleted: bool = False) -> Optional[User]:
        """ユーザー名でユーザーを取得する

        Args:
            db: データベースセッション
            name: ユーザー名
            include_deleted: 削除済みユーザーも含めるかどうか

        Returns:
            Optional[User]: ユーザーオブジェクト（存在しない場合はNone）
        """
        query = db.query(User).filter(User.name == name)
        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))
        return query.first()

    @staticmethod
    def get_user_by_email(db: Session, email: str, include_deleted: bool = False) -> Optional[User]:
        """メールアドレスでユーザーを取得する

        Args:
            db: データベースセッション
            email: メールアドレス
            include_deleted: 削除済みユーザーも含めるかどうか

        Returns:
            Optional[User]: ユーザーオブジェクト（存在しない場合はNone）
        """
        query = db.query(User).filter(User.email == email)
        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))
        return query.first()

    @staticmethod
    def get_all_users(db: Session, include_deleted: bool = False) -> list[User]:
        """全ユーザーを取得する

        Args:
            db: データベースセッション
            include_deleted: 削除済みユーザーも含めるかどうか

        Returns:
            list[User]: ユーザーのリスト（論理削除されていないもの）
        """
        query = db.query(User)
        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))
        return query.all()

    @staticmethod
    def is_name_taken(db: Session, name: str) -> bool:
        """ユーザー名が既に使用されているかチェックする

        Args:
            db: データベースセッション
            name: チェックするユーザー名

        Returns:
            bool: 使用済みの場合True、利用可能な場合False
        """
        return UserService.get_user_by_name(db, name) is not None

    @staticmethod
    def is_email_taken(db: Session, email: str) -> bool:
        """メールアドレスが既に使用されているかチェックする

        Args:
            db: データベースセッション
            email: チェックするメールアドレス

        Returns:
            bool: 使用済みの場合True、利用可能な場合False
        """
        return UserService.get_user_by_email(db, email) is not None

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """パスワードを検証する

        Args:
            plain_password: 平文パスワード
            hashed_password: ハッシュ化済みパスワード

        Returns:
            bool: パスワードが一致する場合True
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """ユーザー情報を更新する

        Args:
            db: データベースセッション
            user_id: 更新対象のユーザーID
            user_data: 更新データ

        Returns:
            Optional[User]: 更新されたユーザーオブジェクト（存在しない場合はNone）

        Raises:
            ValueError: パスワード変更時に現在のパスワードが正しくない場合
            IntegrityError: ユーザー名またはメールアドレスが重複している場合
        """
        # ユーザーの存在確認
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        # パスワード変更の処理
        if user_data.new_password is not None:
            if not user_data.current_password:
                raise ValueError("パスワード変更には現在のパスワードが必要です")

            if not UserService.verify_password(
                user_data.current_password, user.password
            ):
                raise ValueError("現在のパスワードが正しくありません")

            # 新しいパスワードをハッシュ化
            user.password = pwd_context.hash(user_data.new_password)

        # 名前の更新（重複チェック付き）
        if user_data.name is not None and user_data.name != user.name:
            if UserService.is_name_taken(db, user_data.name):
                raise IntegrityError("ユーザー名が既に使用されています", None, None)
            user.name = user_data.name

        # メールアドレスの更新（重複チェック付き）
        if user_data.email is not None and user_data.email != user.email:
            if UserService.is_email_taken(db, user_data.email):
                raise IntegrityError("メールアドレスが既に使用されています", None, None)
            user.email = user_data.email

        try:
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise

    @staticmethod
    def soft_delete_user_by_id(db: Session, user_id: int) -> bool:
        """指定されたIDのユーザーを論理削除する

        Args:
            db: データベースセッション
            user_id: 削除対象のユーザーID

        Returns:
            bool: 削除成功の場合True、ユーザーが存在しない場合False
        """
        user = UserService.get_user_by_id(db, user_id, include_deleted=False)
        if not user:
            return False

        try:
            user.soft_delete()
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def hard_delete_user_by_id(db: Session, user_id: int) -> bool:
        """指定されたIDのユーザーを物理削除する

        Args:
            db: データベースセッション
            user_id: 削除対象のユーザーID

        Returns:
            bool: 削除成功の場合True、ユーザーが存在しない場合False
        """
        user = UserService.get_user_by_id(db, user_id, include_deleted=True)
        if not user:
            return False

        try:
            db.delete(user)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def restore_user_by_id(db: Session, user_id: int) -> bool:
        """指定されたIDのユーザーを復元する

        Args:
            db: データベースセッション
            user_id: 復元対象のユーザーID

        Returns:
            bool: 復元成功の場合True、ユーザーが存在しない場合False
        """
        user = UserService.get_user_by_id(db, user_id, include_deleted=True)
        if not user or not user.is_deleted:
            return False

        try:
            user.deleted_at = None
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def soft_delete_all_users(db: Session) -> int:
        """全ユーザーを論理削除する

        Args:
            db: データベースセッション

        Returns:
            int: 削除されたユーザー数

        Raises:
            Exception: 削除処理中にエラーが発生した場合
        """
        try:
            # アクティブな全ユーザーを取得して論理削除
            users = UserService.get_all_users(db, include_deleted=False)
            deleted_count = len(users)

            for user in users:
                user.soft_delete()

            db.commit()
            return deleted_count
        except Exception:
            db.rollback()
            raise

    # 下位互換性のためのエイリアス
    @staticmethod
    def delete_user_by_id(db: Session, user_id: int) -> bool:
        """指定されたIDのユーザーを削除する（論理削除）

        Note: 下位互換性のために残されています。soft_delete_user_by_idの使用を推奨します。
        """
        return UserService.soft_delete_user_by_id(db, user_id)

    @staticmethod
    def delete_all_users(db: Session) -> int:
        """全ユーザーを削除する（論理削除）

        Note: 下位互換性のために残されています。soft_delete_all_usersの使用を推奨します。
        """
        return UserService.soft_delete_all_users(db)
