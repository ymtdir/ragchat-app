# RAG Chat API - Backend

[![Backend Coverage](https://codecov.io/gh/ymtdir/ragchat-app/branch/main/graph/badge.svg?flag=backend)](https://codecov.io/gh/ymtdir/ragchat-app)

FastAPI + ChromaDB を使ったベクトル検索 API

## 🛠️ 技術スタック

- **Framework**: FastAPI
- **Vector DB**: ChromaDB
- **Embedding**: SentenceTransformer (multilingual-e5-large)
- **Language**: Python 3.12

## 🚀 開発環境セットアップ

### 前提条件

- Python 3.12 以上がインストールされていること
- Docker と Docker Compose がインストールされていること
- ターミナル環境が使用可能であること
  - Windows: PowerShell または Command Prompt
  - macOS/Linux: Terminal

### 1. 仮想環境の作成と有効化

**Windows:**

```cmd
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt
```

**macOS/Linux:**

```bash
# 仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 2. アプリケーションの起動

プロジェクト全体は Docker で起動します。詳細は、ルートディレクトリの`README.md`を参照してください。

### 3. アクセス先

| サービス   | URL                         |
| ---------- | --------------------------- |
| API        | http://localhost:8000       |
| API 仕様書 | http://localhost:8000/docs  |
| ReDoc      | http://localhost:8000/redoc |

## ⚙️ 環境変数設定

### 主要な設定項目

| 環境変数名               | デフォルト値                     | 説明                         |
| ------------------------ | -------------------------------- | ---------------------------- |
| `DEBUG`                  | `false`                          | デバッグモードの有効化       |
| `EMBEDDING_MODEL_NAME`   | `intfloat/multilingual-e5-large` | 使用する Embedding モデル    |
| `VECTOR_DB_PATH`         | `./vector_db`                    | ChromaDB の保存パス          |
| `COLLECTION_NAME`        | `documents`                      | コレクション名               |
| `DEFAULT_SEARCH_RESULTS` | `5`                              | デフォルト検索結果数（1-50） |
| `MAX_SEARCH_RESULTS`     | `50`                             | 最大検索結果数               |
| `MAX_TEXT_LENGTH`        | `10000`                          | 最大テキスト長               |

## 🧪 テスト・品質管理

### テスト実行

**すべてのテストを実行:**

```bash
# 仮想環境を有効化してから実行
python -m pytest
```

**カバレッジ付きでテスト実行:**

```bash
python -m pytest --cov=app --cov-report=html --cov-report=term
```

**カバレッジの詳細実行方法:**

```bash
# 基本的なカバレッジ実行
python -m pytest --cov=app --cov-report=term

# HTMLレポート付きカバレッジ実行
python -m pytest --cov=app --cov-report=term --cov-report=html

# 特定のモジュールのカバレッジ確認
python -m pytest --cov=app.services.memberships --cov-report=term
python -m pytest --cov=app.models --cov-report=term
python -m pytest --cov=app.routers --cov-report=term

# カバレッジの閾値を設定（70%未満で失敗）
python -m pytest --cov=app --cov-fail-under=70

# HTMLレポートの確認
# htmlcov/index.html をブラウザで開く
```

**特定のテストファイルを実行:**

```bash
python -m pytest tests/test_health.py -v
```

**特定のテスト関数を実行:**

```bash
python -m pytest tests/test_health.py::test_health_check -v
```

### リント実行

**flake8 によるコード品質チェック:**

```bash
flake8 app/ tests/
```

**特定のディレクトリをチェック:**

```bash
flake8 app/
```

**注意:** flake8 の設定は `.flake8` ファイルで管理されており、最大行長は 88 文字に設定されています。

### フォーマット

**black による自動フォーマット:**

```bash
# コードのフォーマット実行
black app/ tests/

# フォーマットのチェックのみ（変更しない）
black --check app/ tests/

# 差分表示
black --diff app/ tests/
```

**注意:** black の設定は `pyproject.toml` ファイルで管理されており、行長は 88 文字、Python 3.12 対応に設定されています。

## 🧪 API テスト

### 基本的な使用例

```bash
# ヘルスチェック
curl http://localhost:8000/

# 文書追加
curl -X POST "http://localhost:8000/api/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "doc_001",
    "title": "サンプル文書",
    "text": "これはサンプル文書です。FastAPIとChromaDBを使用しています。"
  }'

# 文書検索
curl -X POST "http://localhost:8000/api/documents/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "FastAPIについて教えて",
    "n_results": 3
  }'

# 全文書取得
curl http://localhost:8000/api/documents

# コレクション情報取得
curl http://localhost:8000/api/documents/info
```

## 📁 プロジェクト構造

```
backend/
├── app/
│   ├── config/          # 設定管理
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── logging.py
│   │   └── settings.py
│   ├── models/          # データベースモデル
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── group.py
│   ├── schemas/         # APIスキーマ
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── groups.py
│   │   └── documents.py
│   ├── services/        # ビジネスロジック
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── groups.py
│   │   └── documents.py
│   ├── routers/         # APIエンドポイント
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── groups.py
│   │   └── documents.py
│   └── main.py          # FastAPIアプリケーション
├── tests/               # テストコード
├── vector_db/           # ChromaDBデータ（自動生成）
├── .env                 # 環境変数（.env.exampleからコピー）
├── .env.example         # 環境変数のサンプル
├── requirements.txt     # Python依存関係
├── Dockerfile          # Docker設定
└── README.md           # このファイル
```

## 🔧 開発 Tips

### モデルの初回ダウンロード

初回起動時は、SentenceTransformer モデルのダウンロードが発生します：

**Windows:**

```cmd
# 初回起動時（時間がかかります）
uvicorn app.main:app --reload

# ダウンロード先（キャッシュ）
# C:\Users\{ユーザー名}\.cache\huggingface\transformers\
```

**macOS/Linux:**

```bash
# 初回起動時（時間がかかります）
uvicorn app.main:app --reload

# ダウンロード先（キャッシュ）
# ~/.cache/huggingface/transformers/
```

### デバッグモード

```cmd
# .envでDEBUG=trueに設定すると詳細ログが出力
DEBUG=true
```

### ChromaDB データのリセット

**Windows:**

```cmd
# PowerShell
Remove-Item -Recurse -Force vector_db\

# または Command Prompt
rmdir /s /q vector_db
```

**macOS/Linux:**

```bash
# vector_dbフォルダを削除してリセット
rm -rf vector_db/
```

## 🐳 Docker での起動

通常はプロジェクト全体を Docker Compose で起動します。詳細は、ルートディレクトリの`README.md`を参照してください。

個別でバックエンドのみを Docker で起動する場合：

```bash
# イメージのビルド
docker build -t ragchat-backend .

# コンテナの起動
docker run -p 8000:8000 ragchat-backend
```
