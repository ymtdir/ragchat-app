# RAG Chat App

[![Backend Coverage](https://codecov.io/gh/ymtdir/ragchat-app/branch/main/graph/badge.svg?flag=backend)](https://codecov.io/gh/ymtdir/ragchat-app)
[![Frontend Coverage](https://codecov.io/gh/ymtdir/ragchat-app/branch/main/graph/badge.svg?flag=frontend)](https://codecov.io/gh/ymtdir/ragchat-app)

FastAPI × React × PostgreSQL × ChromaDB を使った RAG チャットアプリケーション

> **全体統合開発用の手順です。個別開発は各ディレクトリの README を参照してください。**
>
> - バックエンド個別開発: [backend/README.md](backend/README.md)
> - フロントエンド個別開発: [frontend/README.md](frontend/README.md)

## 🛠️ 技術スタック

### バックエンド

- **Framework**: FastAPI
- **Language**: Python 3.12
- **Vector DB**: ChromaDB
- **Embedding**: SentenceTransformer (multilingual-e5-large)
- **Database**: PostgreSQL
- **Testing**: pytest + pytest-cov
- **Code Quality**: black + flake8

### フロントエンド

- **Framework**: React 19
- **Language**: TypeScript
- **Build Tool**: Vite
- **Testing**: Vitest + React Testing Library
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI
- **Code Quality**: Prettier + ESLint

### インフラ・ツール

- **Database**: PostgreSQL + pgAdmin
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Code Coverage**: Codecov

## 🚀 Docker Compose での起動方法

全体統合環境での起動手順です。

### 前提条件

- Docker と Docker Compose がインストールされていること
- Git がインストールされていること
- ターミナル環境が使用可能であること

### 1. リポジトリのクローン

```bash
git clone https://github.com/ymtdir/ragchat-app.git
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

## 📁 プロジェクト構造

```
ragchat-app/
├── backend/                 # FastAPI バックエンド
│   ├── app/
│   │   ├── config/         # 設定管理
│   │   ├── models/         # データベースモデル
│   │   ├── routers/        # API エンドポイント
│   │   ├── schemas/        # API スキーマ
│   │   ├── services/       # ビジネスロジック
│   │   └── main.py         # FastAPI アプリケーション
│   ├── tests/              # テストコード
│   ├── vector_db/          # ChromaDB データ（自動生成）
│   ├── .flake8            # flake8 設定
│   ├── pyproject.toml     # black 設定
│   ├── requirements.txt   # Python 依存関係
│   └── README.md          # バックエンド個別 README
├── frontend/               # React フロントエンド
│   ├── src/
│   │   ├── components/    # UI コンポーネント
│   │   ├── hooks/         # カスタムフック
│   │   ├── services/      # API 通信
│   │   ├── types/         # 型定義
│   │   └── utils/         # ユーティリティ関数
│   ├── .prettierrc       # Prettier 設定
│   ├── eslint.config.js  # ESLint 設定
│   ├── package.json      # Node.js 依存関係
│   └── README.md         # フロントエンド個別 README
├── .github/
│   └── workflows/        # GitHub Actions CI/CD
├── docker-compose.yml    # Docker Compose 設定
├── codecov.yml          # Codecov 設定
└── README.md            # このファイル
```

## 🔧 開発 Tips

### 初回セットアップ後の確認

```bash
# 全サービスが正常に起動しているか確認
docker compose ps

# ログの確認
docker compose logs backend
docker compose logs frontend

# データベースの接続確認
docker compose exec db psql -U user -d ragchat -c "\dt"
```

### 開発中のよくある操作

```bash
# 特定のサービスのみ再起動
docker compose restart backend
docker compose restart frontend

# 特定のサービスのログをリアルタイム表示
docker compose logs -f backend

# データベースのリセット
docker compose down -v
docker compose up -d
```

### トラブルシューティング

**ポートが既に使用されている場合:**

```bash
# 使用中のポートを確認
lsof -i :3000  # フロントエンド
lsof -i :8000  # バックエンド
lsof -i :5432  # PostgreSQL
```

**Docker イメージの完全リビルド:**

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

## 📝 現在の状態

- ✅ FastAPI + PostgreSQL + ChromaDB バックエンド
- ✅ React + TypeScript フロントエンド
- ✅ ユーザー認証・管理機能
- ✅ ベクトル検索機能（ChromaDB）
- ✅ CI/CD パイプライン（GitHub Actions）
- ✅ コード品質管理（black、Prettier、ESLint、flake8）
- ✅ テスト環境（pytest、Vitest）
- ✅ コードカバレッジ（Codecov）

**次のステップ:** RAG チャット機能の実装
