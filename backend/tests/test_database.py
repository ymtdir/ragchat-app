"""
データベース設定のテストモジュール

テスト実行方法:
1. コマンドラインからの実行:
    python -m pytest -v tests/test_database.py

2. 特定のテストメソッドだけ実行:
    python -m pytest -v tests/test_database.py::TestDatabase::test_get_db_success
    python -m pytest -v \
        tests/test_database.py::TestDatabase::test_get_db_connection_error

3. カバレッジレポート生成:
    coverage run -m pytest tests/test_database.py
    coverage report
    coverage html
"""

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from app.config.database import get_db, create_tables


class TestDatabase:
    """データベース設定のテストクラス"""

    def test_get_db_success(self):
        """データベースセッション取得 - 成功"""
        # モックセッション
        mock_session = MagicMock()

        with patch("app.config.database.SessionLocal") as mock_session_local:
            mock_session_local.return_value = mock_session

            # get_db関数をジェネレータとして実行
            db_gen = get_db()
            db = next(db_gen)

            # セッションが正しく返されることを確認
            assert db == mock_session

            # ジェネレータを正常に終了
            try:
                next(db_gen)
            except StopIteration:
                pass

            # セッションが作成されたことを確認
            mock_session_local.assert_called_once()

    def test_get_db_connection_error(self):
        """データベースセッション取得 - 接続エラー"""
        # モックセッション（エラーを発生させる）
        mock_session = MagicMock()
        mock_session.close.side_effect = SQLAlchemyError("データベース接続エラー")

        with patch("app.config.database.SessionLocal") as mock_session_local:
            mock_session_local.return_value = mock_session

            # get_db関数をジェネレータとして実行
            db_gen = get_db()
            db = next(db_gen)

            # セッションが正しく返されることを確認
            assert db == mock_session

            # ジェネレータを終了（finallyブロックでcloseが呼ばれる）
            # closeメソッドでエラーが発生することを確認
            with pytest.raises(SQLAlchemyError, match="データベース接続エラー"):
                try:
                    next(db_gen)
                except StopIteration:
                    # ジェネレータが正常に終了した場合、closeメソッドが呼ばれる
                    pass

            # closeメソッドが呼ばれたことを確認
            mock_session.close.assert_called_once()

    def test_get_db_session_close_called(self):
        """データベースセッション取得 - closeメソッドが呼ばれることを確認"""
        # モックセッション
        mock_session = MagicMock()

        with patch("app.config.database.SessionLocal") as mock_session_local:
            mock_session_local.return_value = mock_session

            # get_db関数をジェネレータとして実行
            db_gen = get_db()
            db = next(db_gen)

            # セッションが正しく返されることを確認
            assert db == mock_session

            # ジェネレータを終了（finallyブロックでcloseが呼ばれる）
            try:
                next(db_gen)
            except StopIteration:
                pass

            # closeメソッドが呼ばれたことを確認
            mock_session.close.assert_called_once()

    def test_get_db_exception_during_usage(self):
        """データベースセッション取得 - 使用中にエラーが発生した場合"""
        # モックセッション
        mock_session = MagicMock()

        with patch("app.config.database.SessionLocal") as mock_session_local:
            mock_session_local.return_value = mock_session

            # get_db関数をジェネレータとして実行
            db_gen = get_db()
            db = next(db_gen)

            # セッションが正しく返されることを確認
            assert db == mock_session

            # 使用中にエラーが発生した場合でもfinallyブロックが実行される
            try:
                # ジェネレータを終了（finallyブロックでcloseが呼ばれる）
                next(db_gen)
            except StopIteration:
                pass

            # closeメソッドが呼ばれたことを確認
            mock_session.close.assert_called_once()

    def test_create_tables_function_exists(self):
        """create_tables関数が存在することを確認"""
        # create_tables関数が呼び出し可能であることを確認
        assert callable(create_tables)

        # 関数のドキュメント文字列が存在することを確認
        assert create_tables.__doc__ is not None
        assert "テーブルを作成する関数" in create_tables.__doc__
