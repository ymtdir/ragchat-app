# RAG Chat API - Backend

[![Backend Coverage](https://codecov.io/gh/ymtdir/ragchat-app/branch/main/graph/badge.svg?flag=backend)](https://codecov.io/gh/ymtdir/ragchat-app)

FastAPI + ChromaDB を使ったベクトル検索 API

## 🛠️ 技術スタック

- **Framework**: FastAPI
- **Vector DB**: ChromaDB
- **Embedding**: SentenceTransformer (multilingual-e5-large)
- **Language**: Python 3.12

## 🚀 個別開発での起動方法

バックエンドのみを開発する場合の手順です。

### 前提条件

- Python 3.12 以上がインストールされていること
- ターミナル環境が使用可能であること
  - Windows: PowerShell または Command Prompt
  - macOS/Linux: Terminal

### 1. 環境設定

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

### 2. 設定ファイルの準備

`.env.example`をコピーして設定ファイルを作成します。

**Windows:**

```cmd
# .env.exampleを.envにコピー
copy .env.example .env

# 必要に応じて.envファイルの内容を編集
notepad .env
```

**macOS/Linux:**

```bash
# .env.exampleを.envにコピー
cp .env.example .env

# 必要に応じて.envファイルの内容を編集
nano .env
# または
vim .env
```

**Windows (コマンドプロンプト):**

```cmd
copy .env.example .env
```

**Windows (PowerShell):**

```powershell
cp .env.example .env
```

**macOS/Linux:**

```bash
cp .env.example .env
```

### 3. アプリケーションの起動

**Windows:**

```cmd
# 開発サーバーの起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**macOS/Linux:**

```bash
# 開発サーバーの起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. アクセス先

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

### その他の設定項目（オプション）

設定ファイル（`app/config/settings.py`）で定義されている他の項目も環境変数で上書き可能です：

```
# アプリケーション情報
APP_NAME=RAG Chat API
APP_VERSION=1.0.0

# ChromaDB詳細設定
COLLECTION_NAME=documents
COLLECTION_DESCRIPTION=文書の特徴量を保存するコレクション

# 検索制限設定
MAX_SEARCH_RESULTS=50
MAX_TEXT_LENGTH=10000
```

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
│   │   └── settings.py
│   ├── schemas/         # APIスキーマ
│   │   ├── __init__.py
│   │   └── vector.py
│   ├── services/        # ビジネスロジック
│   │   ├── __init__.py
│   │   └── vector.py
│   └── main.py          # FastAPIアプリケーション
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

個別で Docker を使用する場合：

**Windows:**

```cmd
# イメージのビルド
docker build -t ragchat-backend .

# コンテナの起動（PowerShell）
docker run -p 8000:8000 -v ${PWD}:/app ragchat-backend

# または Command Prompt
docker run -p 8000:8000 -v %cd%:/app ragchat-backend
```

**macOS/Linux:**

```bash
# イメージのビルド
docker build -t ragchat-backend .

# コンテナの起動
docker run -p 8000:8000 -v $(pwd):/app ragchat-backend
```

**注意**: プロジェクト全体での起動は、ルートディレクトリの`README.md`を参照してください。
