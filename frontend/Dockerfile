FROM node:20

WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package.json package-lock.json* ./

# 依存関係をインストール
RUN npm ci

# ソースコードをコピー
COPY . .

# ポート3000を公開
EXPOSE 3000

# 開発サーバーを起動（--hostでDocker環境に対応）
CMD ["npm", "run", "dev"] 
