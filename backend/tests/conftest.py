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

import pytest
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
    # テーブル作成
    Base.metadata.create_all(bind=engine)

    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def db(db_session):
    """既存のテスト用の互換性のための別名"""
    return db_session


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPIアプリケーション用のテストクライアント（共有セッション）"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    # 依存性オーバーライドをクリア
    app.dependency_overrides.clear()
