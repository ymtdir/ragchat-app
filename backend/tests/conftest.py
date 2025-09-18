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


@pytest.fixture
def db():
    """テスト用データベースセッション

    各テスト実行前にテーブルを作成し、実行後にクリーンアップします。

    Returns:
        SQLAlchemy セッション
    """
    # テーブル作成
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # テストデータをクリーンアップ
        Base.metadata.drop_all(bind=engine)


def override_get_db():
    """データベース依存性をテスト用にオーバーライド"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """FastAPIアプリケーション用のテストクライアントを作成

    FastAPIアプリケーションに対してHTTPリクエストを送信するための
    TestClientインスタンスを提供するフィクスチャです。

    Returns:
        設定済みのFastAPIアプリ用テストクライアント

    使用例:
        def test_endpoint(client):
            response = client.get("/")
            assert response.status_code == 200
    """
    # テーブル作成
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as client:
        yield client

    # テストデータをクリーンアップ
    Base.metadata.drop_all(bind=engine)
