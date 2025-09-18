"""
Pytest設定とフィクスチャ

FastAPIアプリケーションのテスト用設定とフィクスチャを定義します。

注意事項:
    ファイル名'conftest.py'はpytestの規約で固定されており、変更できません。
    pytestがこのファイルを自動で発見・読み込みします。

実行方法:
    cd backend
    pip install -r requirements.txt
    python -m pytest tests/test_health.py -v
"""

import os
import pytest
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.config.database import get_db, Base

# テスト用データベース設定
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """テスト用データベースセッション（トランザクション管理）"""
    # 各テストで独立したデータベースファイルを使用
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        test_db_url = f"sqlite:///{tmp_file.name}"

        # テスト用エンジンを作成
        test_engine = create_engine(
            test_db_url, connect_args={"check_same_thread": False}
        )
        TestSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=test_engine
        )

        # テーブル作成
        Base.metadata.create_all(bind=test_engine)

        connection = test_engine.connect()
        transaction = connection.begin()
        session = TestSessionLocal(bind=connection)

        try:
            yield session
        finally:
            session.close()
            transaction.rollback()
            connection.close()
            # テスト用データベースファイルを削除
            try:
                os.unlink(tmp_file.name)
            except OSError:
                pass


@pytest.fixture(scope="function")
def db(db_session):
    """既存のテスト用の互換性のための別名"""
    return db_session


@pytest.fixture(scope="function")
def client():
    """FastAPIアプリケーション用のテストクライアント（独立セッション）"""
    # 各テストで独立したデータベースファイルを使用
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        test_db_url = f"sqlite:///{tmp_file.name}"

        # テスト用エンジンを作成
        test_engine = create_engine(
            test_db_url, connect_args={"check_same_thread": False}
        )
        TestSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=test_engine
        )

        # すべてのモデルをインポートしてテーブルを作成
        from app.models.user import User  # noqa: F401
        from app.models.group import Group  # noqa: F401
        from app.models.membership import Membership  # noqa: F401

        # テーブル作成
        Base.metadata.create_all(bind=test_engine)

        def override_get_db():
            connection = test_engine.connect()
            transaction = connection.begin()
            session = TestSessionLocal(bind=connection)
            try:
                yield session
            finally:
                session.close()
                transaction.rollback()
                connection.close()

        app.dependency_overrides[get_db] = override_get_db

        with TestClient(app) as client:
            yield client

        # 依存性オーバーライドをクリア
        app.dependency_overrides.clear()

        # テスト用データベースファイルを削除
        try:
            os.unlink(tmp_file.name)
        except OSError:
            pass
