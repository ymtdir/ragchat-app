# RAG Chat App

FastAPI × React × PostgreSQL を使った RAG チャットアプリケーション

## 🛠️ 技術スタック

- **Backend**: FastAPI
- **Frontend**: React + Vite
- **Database**: PostgreSQL + pgAdmin

## 🚀 起動方法

```bash
git clone <repository-url>
cd ragchat-app
docker compose up -d --build
```

## 🌐 アクセス先

| サービス         | URL                        |
| ---------------- | -------------------------- |
| フロントエンド   | http://localhost:3000      |
| バックエンド API | http://localhost:8000      |
| API 仕様書       | http://localhost:8000/docs |
| pgAdmin          | http://localhost:8080      |

## 🔐 ログイン情報

**pgAdmin**

- Email: `admin@example.com`
- Password: `admin`

**PostgreSQL**

- Host: `db` (コンテナ間) / `localhost` (外部)
- Database: `ragchat`
- User: `user`
- Password: `password`

## 📝 現在の状態

最低限の実装（Hello World）から開始。段階的に機能を拡張予定。
