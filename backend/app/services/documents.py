"""
文書管理サービス

テキストの特徴量を算出し、ChromaDBに保存する機能を提供します。

このモジュールでは、SentenceTransformerを使用した日本語対応の
ベクトル化機能とChromaDBを使った永続化機能を提供しています。

主な機能:
    - テキストのベクトル化（多言語対応）
    - ベクトル類似度検索
    - 文書の永続化（ChromaDB）
    - CRUD操作（作成、読み取り、更新、削除）

Typical usage example:
    service = DocumentService()
    result = await service.add_document(
        id="doc_001",
        title="サンプル",
        text="これはサンプル文書です。"
    )
"""

import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from ..config import settings
from ..config.logging import get_logger
import datetime

logger = get_logger(__name__)


class DocumentService:
    """文書管理サービスクラス

    テキストをベクトルに変換し、ChromaDBに保存する機能を提供します。

    このクラスは、SentenceTransformerを使用してテキストをベクトル化し、
    ChromaDBに永続化する機能を提供します。日本語を含む多言語に対応しています。

    Attributes:
        embedding_model: SentenceTransformerモデルインスタンス
        chroma_client: ChromaDBクライアントインスタンス
        collection: 文書を保存するコレクション
    """

    def __init__(self):
        """DocumentServiceの初期化

        SentenceTransformerとChromaDBクライアントを初期化します。
        日本語対応の多言語モデル'intfloat/multilingual-e5-large'を使用します。

        Note:
            初期化時にモデルのダウンロードが発生する場合があります。
            初回実行時は時間がかかることがあります。
        """
        logger.info("DocumentService初期化開始")

        # 日本語に対応したEmbeddingモデルを使用
        self.embedding_model = SentenceTransformer(settings.embedding_model_name)

        # ChromaDBクライアントの初期化
        self.chroma_client = chromadb.PersistentClient(path=settings.vector_db_path)

        # コレクション（テーブルのようなもの）を取得または作成
        self.collection = self.chroma_client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"description": settings.collection_description},
        )

        logger.info("DocumentService初期化完了")

    async def add_document(self, id: str, title: str, text: str) -> Dict[str, Any]:
        """文書をベクトル化してDBに保存

        指定された文書をベクトル化し、ChromaDBに保存します。
        同じIDが存在する場合は上書きされます。

        Args:
            id: 文書の一意識別子
            title: 文書のタイトル
            text: ベクトル化するテキスト内容

        Returns:
            保存された文書のIDとベクトル情報を含む辞書
            {
                "vector_id": str,  # 保存された文書のID
                "embedding": List[float]  # 生成されたベクトル
            }

        Raises:
            Exception: ベクトル化またはDB保存に失敗した場合

        Example:
            result = await service.add_document(
                id="doc_001",
                title="サンプル文書",
                text="これはサンプルです。"
            )
        """
        try:
            logger.info(f"ベクトル化開始: ID={id}")

            # 既存データの確認
            existing = self.collection.get(ids=[id])
            if existing["ids"]:
                logger.debug(f"既存データが見つかりました: {existing}")
            else:
                logger.debug("新規データです")

            # テキストをベクトルに変換
            embedding = self.embedding_model.encode([text])[0].tolist()
            logger.info(f"ベクトル化完了: 次元数={len(embedding)}")

            # メタデータの準備
            doc_metadata = {
                "title": title,
                "created_at": datetime.datetime.now().isoformat(),
                "text_length": len(text),
            }

            logger.debug("ChromaDBへの保存開始")

            # upsertを使用して確実に上書き
            self.collection.upsert(
                embeddings=[embedding],
                documents=[text],
                metadatas=[doc_metadata],
                ids=[id],
            )

            logger.info(f"ChromaDBへの保存完了: {id}")

            # 保存後の確認
            saved_data = self.collection.get(ids=[id])
            logger.debug(f"保存後確認: {saved_data}")

            return {"vector_id": id, "embedding": embedding}

        except Exception as e:
            logger.error(f"文書保存エラー: {str(e)}")
            raise Exception(f"文書の保存に失敗しました: {str(e)}")

    async def search_similar_documents(
        self, query: str, n_results: int = settings.default_search_results
    ) -> List[Dict[str, Any]]:
        """類似文書を検索

        指定されたクエリに類似した文書をベクトル検索で取得します。
        コサイン類似度を使用して類似度を計算します。

        Args:
            query: 検索クエリ文字列
            n_results: 取得する結果数（デフォルト: 5）

        Returns:
            類似文書のリスト。各要素は以下の形式:
            {
                "id": str,  # 文書ID
                "title": str,  # 文書タイトル
                "text": str,  # 文書内容
                "similarity_score": float  # 類似度スコア（0.0-1.0）
            }

        Raises:
            Exception: 検索処理に失敗した場合

        Example:
            results = await service.search_similar_documents(
                query="機械学習について",
                n_results=3
            )
        """
        try:
            logger.info("類似文書検索開始")

            # クエリをベクトル化
            query_embedding = self.embedding_model.encode([query])[0].tolist()

            # 類似文書を検索
            results = self.collection.query(
                query_embeddings=[query_embedding], n_results=n_results
            )

            # 結果を整形
            similar_docs = []
            for i in range(len(results["ids"][0])):
                similar_docs.append(
                    {
                        "id": results["ids"][0][i],
                        "title": results["metadatas"][0][i].get("title", "無題"),
                        "text": results["documents"][0][i],
                        "similarity_score": 1 - results["distances"][0][i],
                    }
                )

            logger.info(f"類似文書検索完了: {len(similar_docs)}件")

            return similar_docs

        except Exception as e:
            logger.error(f"類似文書検索エラー: {str(e)}")
            raise Exception(f"類似文書の検索に失敗しました: {str(e)}")

    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """保存されている全ての文書を取得

        ChromaDBに保存されている全文書を取得します。

        Returns:
            全文書のリスト。各要素は以下の形式:
            {
                "id": str,  # 文書ID
                "title": str,  # 文書タイトル
                "text": str,  # 文書内容
                "similarity_score": float  # 1.0（全件取得のため）
            }

        Raises:
            Exception: 取得処理に失敗した場合

        Example:
            all_docs = await service.get_all_documents()
        """
        try:
            logger.info("全文書取得開始")

            # コレクションの全データを取得
            results = self.collection.get()

            # 結果を整形
            all_docs = []
            for i in range(len(results["ids"])):
                all_docs.append(
                    {
                        "id": results["ids"][i],
                        "title": results["metadatas"][i].get("title", "無題"),
                        "text": results["documents"][i],
                        "similarity_score": 1.0,  # 全件取得なので類似度は1.0
                    }
                )

            logger.info(f"全文書取得完了: {len(all_docs)}件")

            return all_docs

        except Exception as e:
            logger.error(f"全文書取得エラー: {str(e)}")
            raise Exception(f"文書の取得に失敗しました: {str(e)}")

    async def get_collection_info(self) -> Dict[str, Any]:
        """コレクションの情報を取得

        ChromaDBコレクションの基本情報を取得します。

        Returns:
            コレクション情報を含む辞書:
            {
                "collection_name": str,  # コレクション名
                "document_count": int,  # 文書数
                "storage_type": str,  # ストレージタイプ
                "path": str  # ストレージパス
            }

        Raises:
            Exception: 情報取得に失敗した場合

        Example:
            info = await service.get_collection_info()
        """
        try:
            # コレクションの基本情報
            collection_info = {
                "collection_name": self.collection.name,
                "document_count": self.collection.count(),
                "storage_type": "local_persistent",
                "path": settings.vector_db_path,
            }

            return collection_info

        except Exception as e:
            raise Exception(f"コレクション情報の取得に失敗しました: {str(e)}")

    async def delete_document(self, document_id: str) -> bool:
        """指定されたIDの文書を削除

        ChromaDBから指定されたIDの文書を削除します。

        Args:
            document_id: 削除する文書の一意識別子

        Returns:
            削除が成功した場合True

        Raises:
            Exception: 削除処理に失敗した場合

        Example:
            success = await service.delete_document("doc_001")
        """
        try:
            logger.info(f"文書削除開始: {document_id}")

            self.collection.delete(ids=[document_id])

            logger.info(f"文書削除完了: {document_id}")

            return True

        except Exception as e:
            logger.error(f"文書削除エラー: {str(e)}")
            raise Exception(f"文書の削除に失敗しました: {str(e)}")

    async def delete_all_documents(self) -> Dict[str, Any]:
        """保存されている全ての文書を削除

        ChromaDBコレクション内の全文書を削除します。
        開発・テスト用途での使用を想定しています。

        Returns:
            削除結果を含む辞書:
            {
                "success": bool,  # 削除成功フラグ
                "deleted_count": int  # 削除された文書数
            }

        Raises:
            Exception: 削除処理に失敗した場合

        Warning:
            この操作は元に戻せません。本番環境での使用は注意してください。

        Example:
            result = await service.delete_all_documents()
        """
        try:
            logger.info("全文書削除開始")

            # 削除前の文書数を取得
            count_before = self.collection.count()

            # 全文書を取得してIDのリストを作成
            all_docs = self.collection.get()
            all_ids = all_docs["ids"]

            if all_ids:
                # 全IDを指定して一括削除
                self.collection.delete(ids=all_ids)

            # 削除後の文書数を確認
            count_after = self.collection.count()
            deleted_count = count_before - count_after

            logger.info(f"全文書削除完了: {deleted_count}件削除")

            return {"success": True, "deleted_count": deleted_count}

        except Exception as e:
            logger.error(f"全文書削除エラー: {str(e)}")
            raise Exception(f"全文書の削除に失敗しました: {str(e)}")

    async def get_document(self, document_id: str) -> Dict[str, Any]:
        """指定されたIDの文書を取得

        ChromaDBから指定されたIDの文書を取得します。

        Args:
            document_id: 取得する文書の一意識別子

        Returns:
            文書情報を含む辞書:
            {
                "id": str,  # 文書ID
                "title": str,  # 文書タイトル
                "text": str,  # 文書内容
                "embedding": None  # 埋め込みベクトル（現在はNone）
            }

        Raises:
            Exception: 文書が見つからない場合や取得に失敗した場合

        Example:
            document = await service.get_document("doc_001")
        """
        try:
            logger.info(f"個別文書取得開始: {document_id}")

            # 指定されたIDの文書を取得
            results = self.collection.get(ids=[document_id])

            if not results["ids"]:
                raise Exception(f"ID {document_id} の文書が見つかりません")

            # 結果を整形
            document = {
                "id": results["ids"][0],
                "title": results["metadatas"][0].get("title", ""),
                "text": results["documents"][0],
                "embedding": None,  # 実際の実装では埋め込みベクトルを返す
            }

            logger.info(f"個別文書取得完了: {document_id}")

            return document

        except Exception as e:
            logger.error(f"個別文書取得エラー: {str(e)}")
            raise Exception(f"文書の取得に失敗しました: {str(e)}")


def get_documents_service() -> DocumentService:
    """DocumentServiceのインスタンスを取得

    Dependency Injection用のファクトリ関数です。
    FastAPIの依存性注入システムで使用されます。

    Returns:
        DocumentServiceの新しいインスタンス

    Example:
        service = get_documents_service()
    """
    return DocumentService()
