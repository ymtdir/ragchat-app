# RAG Chat App - Frontend

[![Frontend Coverage](https://codecov.io/gh/ymtdir/ragchat-app/branch/main/graph/badge.svg?flag=frontend)](https://codecov.io/gh/ymtdir/ragchat-app)

React + TypeScript + Vite を使ったモダンなフロントエンドアプリケーション

## 🛠️ 技術スタック

- **Framework**: React 19
- **Language**: TypeScript
- **Build Tool**: Vite
- **Testing**: Vitest + React Testing Library
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI
- **State Management**: React Hooks
- **Routing**: React Router

## 🚀 開発環境セットアップ

### 前提条件

- Node.js 18 以上がインストールされていること
- npm または yarn がインストールされていること
- Docker と Docker Compose がインストールされていること
- ターミナル環境が使用可能であること

### 1. 依存関係のインストール

```bash
npm install
```

### 2. アプリケーションの起動

プロジェクト全体は Docker で起動します。詳細は、ルートディレクトリの`README.md`を参照してください。

### 3. アクセス先

| サービス       | URL                   |
| -------------- | --------------------- |
| フロントエンド | http://localhost:3000 |
| 開発サーバー   | http://localhost:5173 |

## 🧪 テスト・品質管理

### テスト実行

**すべてのテストを実行:**

```bash
npm run test
```

**UI モードでテスト実行:**

```bash
npm run test:ui
```

**カバレッジ付きでテスト実行:**

```bash
npm run test:coverage
```

### リント実行

**ESLint によるコード品質チェック:**

```bash
npm run lint
```

**特定のファイルをチェック:**

```bash
npx eslint src/components/Button.tsx
```

### フォーマット

**Prettier による自動フォーマット:**

```bash
# コードのフォーマット実行
npm run format

# フォーマットのチェックのみ（変更しない）
npm run format:check

# 特定のファイルをフォーマット
npx prettier --write src/components/Button.tsx
```

**注意:** Prettier の設定は `.prettierrc` ファイルで管理されており、ESLint との連携も設定済みです。

### PR 作成前のワークフロー

プルリクエストを作成する前に、以下の手順を実行してください：

1. **依存関係のインストール**

   ```bash
   npm install
   ```

2. **フォーマットチェック**

   ```bash
   npm run format:check
   ```

3. **リントチェック**

   ```bash
   npm run lint
   ```

4. **テスト実行**

   ```bash
   npm run test:coverage
   ```

5. **ビルドチェック**

   ```bash
   npm run build
   ```

6. **すべてのチェックが通過したら、コミット・プッシュ**
   ```bash
   git add .
   git commit -m "feat: 新機能を追加"
   git push origin feature/branch-name
   ```

## 📁 プロジェクト構造

```
frontend/
├── src/
│   ├── components/      # UIコンポーネント
│   ├── hooks/          # カスタムフック
│   ├── services/       # API通信
│   ├── types/          # 型定義
│   ├── utils/          # ユーティリティ関数
│   └── routes/         # ルーティング設定
├── public/             # 静的ファイル
├── coverage/           # テストカバレッジ（自動生成）
├── dist/               # ビルド出力（自動生成）
├── eslint.config.js    # ESLint設定
├── package.json        # 依存関係とスクリプト
├── tsconfig.json       # TypeScript設定
├── vite.config.ts      # Vite設定
└── README.md           # このファイル
```

## 🔧 開発 Tips

### 開発サーバー起動

```bash
# 開発サーバーを起動（ホットリロード有効）
npm run dev
```

### ビルド

```bash
# 本番用ビルド
npm run build

# ビルド結果をプレビュー
npm run preview
```

### 型生成

```bash
# バックエンドAPIから型定義を生成
npm run generate-types
```

**注意:** 型生成を実行する前に、バックエンド API サーバーが起動していることを確認してください。

## 🐳 Docker での起動

通常はプロジェクト全体を Docker Compose で起動します。詳細は、ルートディレクトリの`README.md`を参照してください。

個別でフロントエンドのみを Docker で起動する場合：

```bash
# イメージのビルド
docker build -t ragchat-frontend .

# コンテナの起動
docker run -p 3000:3000 ragchat-frontend
```
