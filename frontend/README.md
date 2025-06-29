# RAG Chat App - Frontend

[![Frontend Coverage](https://codecov.io/gh/ymtdir/ragchat-app/branch/main/graph/badge.svg?flag=frontend)](https://codecov.io/gh/ymtdir/ragchat-app)

React + Vite を使ったフロントエンドアプリケーション

## 🛠️ 技術スタック

- **Framework**: React 18
- **Build Tool**: Vite
- **Testing**: Vitest + React Testing Library
- **Language**: JavaScript/JSX
- **Package Manager**: npm

## 🚀 個別開発での起動方法

フロントエンドのみを開発する場合の手順です。

### 前提条件

- Node.js 18 以上がインストールされていること
- npm がインストールされていること
- ターミナル環境が使用可能であること
  - Windows: PowerShell または Command Prompt
  - macOS/Linux: Terminal

### 1. Node.js のインストール確認

**Windows/macOS/Linux:**

```bash
# Node.jsバージョン確認
node --version

# npmバージョン確認
npm --version
```

Node.js がインストールされていない場合：

**macOS (Homebrew):**

```bash
brew install node
```

**Windows:**

- [Node.js 公式サイト](https://nodejs.org/) からインストーラーをダウンロード

**Linux (Ubuntu/Debian):**

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 2. 依存関係のインストール

**Windows:**

```cmd
# プロジェクトディレクトリに移動
cd frontend

# 依存関係のインストール
npm install
```

**macOS/Linux:**

```bash
# プロジェクトディレクトリに移動
cd frontend

# 依存関係のインストール
npm install
```

### 3. アプリケーションの起動

**Windows:**

```cmd
# 開発サーバーの起動
npm run dev
```

**macOS/Linux:**

```bash
# 開発サーバーの起動
npm run dev
```

### 4. アクセス先

| サービス             | URL                   |
| -------------------- | --------------------- |
| フロントエンドアプリ | http://localhost:3000 |

## 🧪 テスト実行

### テストコマンド

**基本的なテスト実行:**

```bash
# 通常のテスト（一回実行）
npm test

# ウォッチモードでテスト実行
npm run test:watch

# カバレッジ付きテスト
npm run test:coverage
```

**Windows:**

```cmd
# PowerShell または Command Prompt
npm test
npm run test:coverage
```

**macOS/Linux:**

```bash
npm test
npm run test:coverage
```

### カバレッジレポートの確認

```bash
# カバレッジ実行後、ブラウザでレポート確認
npm run test:coverage

# coverage/index.html をブラウザで開く
```

**Windows:**

```cmd
# PowerShellの場合
start coverage/index.html

# Command Promptの場合
coverage\index.html
```

**macOS:**

```bash
open coverage/index.html
```

**Linux:**

```bash
xdg-open coverage/index.html
```

### テストファイルの場所
