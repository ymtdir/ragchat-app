"""アプリケーション設定

2つのデータベースの接続設定と環境変数を管理します。

データベース構成:
    - PostgreSQL: 構造化データ（ユーザー、認証情報等）
    - ChromaDB: ベクトルデータ（文書埋め込み、セマンティック検索）
"""

from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定クラス"""

    # モデル設定（新形式）
    model_config = ConfigDict(env_file_encoding="utf-8")

    # アプリケーション基本設定
    app_name: str = "RAG Chat API"
    app_version: str = "1.0.0"
    debug: bool = False

    # ログ設定
    log_level: str = Field("INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")

    # データベース設定
    database_url: str = "postgresql://admin:password@localhost:5432/ragchat"

    # ChromaDB設定（ベクトルDB：セマンティック検索）
    vector_db_path: str = "./vector_db"
    collection_name: str = "documents"
    collection_description: str = "文書の特徴量を保存するコレクション"

    # ベクトル化モデル設定
    embedding_model_name: str = "intfloat/multilingual-e5-large"

    # 検索設定
    default_search_results: int = Field(5, ge=1, le=50)
    max_search_results: int = 50
    max_text_length: int = 10000


# グローバル設定インスタンス
settings = Settings()
