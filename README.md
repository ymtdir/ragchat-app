# RAG Chat App

FastAPI × React × PostgreSQL × ChromaDB を使った RAG チャットアプリケーション

> **全体統合開発用の手順です。個別開発は各ディレクトリの README を参照してください。**
>
> - バックエンド個別開発: [backend/README.md](backend/README.md)
> - フロントエンド個別開発: [frontend/README.md](frontend/README.md)

## 🛠️ 技術スタック

- **Backend**: FastAPI + ChromaDB
- **Frontend**: React + Vite
- **Database**: PostgreSQL + pgAdmin
- **Vector DB**: ChromaDB（ベクトル検索）
- **Embedding**: SentenceTransformer

## 🚀 Docker Compose での起動方法

全体統合環境での起動手順です。

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd ragchat-app
```

### 2. 環境設定（オプション）

**Windows (コマンドプロンプト):**

```cmd
# バックエンドの環境変数設定（必要に応じて）
copy backend\.env.example backend\.env

# 設定を編集
notepad backend\.env
```

**Windows (PowerShell):**

```powershell
# バックエンドの環境変数設定（必要に応じて）
cp backend/.env.example backend/.env

# 設定を編集
notepad backend/.env
```

**macOS/Linux:**

```bash
# バックエンドの環境変数設定（必要に応じて）
cp backend/.env.example backend/.env

# 設定を編集
nano backend/.env
```

### 3. 全サービスの起動

**Windows/macOS/Linux 共通:**

```bash
# 初回起動またはビルドが必要な変更後
docker compose up -d --build

# 通常の起動（ビルド不要）
docker compose up -d
```

### 4. サービスの停止

**Windows/macOS/Linux 共通:**

```bash
# サービス停止
docker compose down

# データも含めて完全削除
docker compose down -v
```

## 🌐 アクセス先

| サービス         | URL                        |
| ---------------- | -------------------------- |
| フロントエンド   | http://localhost:3000      |
| バックエンド API | http://localhost:8000      |
| API 仕様書       | http://localhost:8000/docs |
| pgAdmin          | http://localhost:8080      |
| ChromaDB         | http://localhost:8001      |

## 🔐 ログイン情報

**pgAdmin**

- Email: `admin@example.com`
- Password: `admin`

**PostgreSQL**

- Host: `db` (コンテナ間) / `localhost` (外部)
- Database: `ragchat`
- User: `user`
- Password: `password`

## 🧠 ベクトル検索機能

ChromaDB を使ったベクトル検索機能が利用できます。

### 基本操作

```bash
# サンプルドキュメント追加
curl http://localhost:8000/documents/sample

# 類似検索実行
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "FastAPIについて", "top_k": 3}'

# コレクション情報確認
curl http://localhost:8000/collection/info
```

### データ永続化

ベクトルデータは `vector_db/` ディレクトリに永続化されます。

## ⚙️ 環境変数設定

バックエンドの設定は環境変数で変更できます。`backend/.env` ファイルを作成して設定してください。

### 設定例

```bash
# backend/.env
# アプリケーション基本設定
DEBUG=false

# ベクトル化モデル設定
EMBEDDING_MODEL_NAME=intfloat/multilingual-e5-large

# ChromaDB設定
VECTOR_DB_PATH=./vector_db

# 検索設定
DEFAULT_SEARCH_RESULTS=5
```

### 主要な設定項目

| 環境変数名               | デフォルト値                     | 説明                           |
| ------------------------ | -------------------------------- | ------------------------------ |
| `DEBUG`                  | `false`                          | デバッグモードの有効化         |
| `EMBEDDING_MODEL_NAME`   | `intfloat/multilingual-e5-large` | 使用する Embedding モデル      |
| `VECTOR_DB_PATH`         | `./vector_db`                    | ChromaDB の保存パス            |
| `DEFAULT_SEARCH_RESULTS` | `5`                              | デフォルトの検索結果数（1-50） |

## 📝 現在の状態

ChromaDB ベクトル検索機能を実装済み。RAG 機能の拡張が可能な状態。
