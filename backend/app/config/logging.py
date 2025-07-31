"""
ログ設定管理

アプリケーション全体のログ設定を管理します。
コンソールとファイルの両方に出力する設定を提供します。
"""

import logging
import logging.config
import os
from typing import Dict, Any
from .settings import settings


class LoggingConfig:
    """ログ設定クラス

    ログレベル、フォーマット、ハンドラーなどを管理。
    コンソールとファイルの両方に出力します。

    ログレベル基準:
    - DEBUG: 詳細な処理状況、開発/デバッグ用（本番では通常非表示）
    - INFO: 重要な処理の開始/完了、正常動作の記録
    - WARNING: 注意すべき操作（データ上書き、非推奨メソッド使用など）
    - ERROR: エラー発生時、例外処理（exc_info=Trueでスタックトレース付き）
    - CRITICAL: システム停止レベルの重大エラー
    """

    # 基本設定
    LOG_LEVEL = settings.log_level
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILENAME = "logs/app.log"  # 出力先パス

    @classmethod
    def setup_log_directory(cls) -> None:
        """ログディレクトリの作成"""
        log_dir = os.path.dirname(cls.LOG_FILENAME)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

    @classmethod
    def get_logging_config(cls) -> Dict[str, Any]:
        """ログ設定辞書を取得

        Returns:
            Dict[str, Any]: ログ設定辞書
        """
        # ログディレクトリを事前に作成
        cls.setup_log_directory()

        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": cls.LOG_FORMAT,
                },
            },
            "handlers": {
                "console": {  # コンソール出力用
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
                "file": {  # ファイル出力用
                    "formatter": "default",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": cls.LOG_FILENAME,
                    "maxBytes": 1024 * 1024 * 5,  # 5MBでファイルを分割
                    "backupCount": 3,  # 3世代までログを保持
                    "encoding": "utf-8",
                },
            },
            "root": {
                "level": cls.LOG_LEVEL,
                "handlers": ["console", "file"],  # 両方のハンドラーを有効にする
            },
        }


def setup_logging() -> None:
    """ログ設定を初期化

    アプリケーション起動時に呼び出してログ設定を適用します。
    """
    config = LoggingConfig.get_logging_config()
    logging.config.dictConfig(config)

    # 設定完了をログ出力
    logger = logging.getLogger(__name__)
    logger.info(f"ログ設定完了 - レベル: {LoggingConfig.LOG_LEVEL}")


def get_logger(name: str) -> logging.Logger:
    """ロガーを取得

    Args:
        name: ロガー名（通常は __name__ を使用）

    Returns:
        logging.Logger: 設定済みのロガーインスタンス
    """
    return logging.getLogger(name)
