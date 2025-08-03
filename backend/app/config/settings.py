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
    debug: bool = Field(default=False, description="デバッグモード", alias="DEBUG")

    # ログ設定
    log_level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="ログレベル",
        alias="LOG_LEVEL"
    )

    # データベース設定
    database_url: str = Field(
        default="postgresql://admin:password@localhost:5432/ragchat",
        description="データベース接続URL",
        alias="DATABASE_URL"
    )

    # ChromaDB設定（ベクトルDB：セマンティック検索）
    vector_db_path: str = Field(
        default="./vector_db",
        description="ベクトルDBのパス",
        alias="VECTOR_DB_PATH"
    )
    collection_name: str = Field(
        default="documents",
        description="コレクション名",
        alias="COLLECTION_NAME"
    )
    collection_description: str = "文書の特徴量を保存するコレクション"

    # ベクトル化モデル設定
    embedding_model_name: str = Field(
        default="intfloat/multilingual-e5-large",
        description="埋め込みモデル名",
        alias="EMBEDDING_MODEL_NAME"
    )

    # 検索設定
    default_search_results: int = Field(
        default=5,
        ge=1,
        le=50,
        description="デフォルト検索結果数",
        alias="DEFAULT_SEARCH_RESULTS"
    )
    max_search_results: int = Field(
        default=50,
        description="最大検索結果数",
        alias="MAX_SEARCH_RESULTS"
    )
    max_text_length: int = Field(
        default=10000,
        description="最大テキスト長",
        alias="MAX_TEXT_LENGTH"
    )

    # JWT認証設定
    secret_key: str = Field(
        default="your-secret-key-here",
        description="JWT署名用の秘密鍵",
        alias="SECRET_KEY"
    )
    algorithm: str = Field(
        default="HS256",
        description="JWTアルゴリズム",
        alias="ALGORITHM"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="アクセストークンの有効期限（分）",
        alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )


# グローバル設定インスタンス
settings = Settings()
