-- RAG Chat App データベース初期化スクリプト

-- チャット履歴テーブル（将来の拡張用）
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 初期データの挿入（テスト用）
INSERT INTO chat_history (message, response) VALUES 
('Hello', 'Hello! How can I help you today?');

-- テーブル作成完了のログ
\echo 'Database initialization completed.'; 