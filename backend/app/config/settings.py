"""アプリケーション設定

環境変数やハードコーディングされた設定値を管理します。
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定クラス"""

    # アプリケーション基本設定
    app_name: str = "RAG Chat API"
    app_version: str = "1.0.0"
    debug: bool = False

    # ベクトル化モデル設定（開発環境デフォルト）
    embedding_model_name: str = "intfloat/multilingual-e5-large"

    # ChromaDB設定（開発環境デフォルト）
    vector_db_path: str = "./vector_db"
    collection_name: str = "documents"
    collection_description: str = "文書の特徴量を保存するコレクション"

    # 検索設定（制約付き）
    default_search_results: int = Field(5, ge=1, le=50)
    max_search_results: int = 50
    max_text_length: int = 10000

    class Config:
        env_file = "../.env"  # backend/.envを参照
        env_file_encoding = "utf-8"


# グローバル設定インスタンス
settings = Settings()
