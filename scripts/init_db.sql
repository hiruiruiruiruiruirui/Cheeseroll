-- AI Student Study Assistant - Initial Schema DDL
-- Target: PostgreSQL 16+

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- Users
-- ============================================================
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    openid          VARCHAR(128) UNIQUE NOT NULL,
    unionid         VARCHAR(128),
    phone           VARCHAR(20),
    nickname        VARCHAR(100),
    avatar_url      VARCHAR(500),
    role            VARCHAR(20) DEFAULT 'user',
    is_active       BOOLEAN DEFAULT true,
    trial_used      BOOLEAN DEFAULT false,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- Files (uploaded by users, auto-expire after 24h)
-- ============================================================
CREATE TABLE files (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    original_name   VARCHAR(500) NOT NULL,
    file_type       VARCHAR(20) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    cos_key         VARCHAR(500) NOT NULL,
    parse_status    VARCHAR(20) DEFAULT 'pending',
    parsed_text     TEXT,
    expires_at      TIMESTAMPTZ DEFAULT (now() + interval '24 hours'),
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_files_user_id ON files(user_id);

-- ============================================================
-- Records (AI-generated study notes)
-- ============================================================
CREATE TABLE records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_id         UUID REFERENCES files(id) ON DELETE SET NULL,
    title           VARCHAR(500) NOT NULL,
    original_markdown TEXT,
    pdf_cos_key     VARCHAR(500),
    status          VARCHAR(20) DEFAULT 'processing',
    error_message   TEXT,
    share_code      VARCHAR(20) UNIQUE,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_records_user_id ON records(user_id);
CREATE INDEX idx_records_created_at ON records(created_at DESC);
CREATE INDEX idx_records_share_code ON records(share_code) WHERE share_code IS NOT NULL;

-- ============================================================
-- Subscription Plans (seed data)
-- ============================================================
CREATE TABLE subscription_plans (
    id              SERIAL PRIMARY KEY,
    plan_type       VARCHAR(20) UNIQUE NOT NULL,
    name            VARCHAR(100) NOT NULL,
    price_cents     INT NOT NULL,
    duration_days   INT NOT NULL,
    daily_quota     INT NOT NULL,
    features        JSONB NOT NULL DEFAULT '[]',
    is_active       BOOLEAN DEFAULT true
);

-- ============================================================
-- User Subscriptions
-- ============================================================
CREATE TABLE subscriptions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_type       VARCHAR(20) NOT NULL,
    status          VARCHAR(20) DEFAULT 'active',
    start_date      TIMESTAMPTZ NOT NULL,
    end_date        TIMESTAMPTZ NOT NULL,
    daily_quota     INT DEFAULT 10,
    daily_used      INT DEFAULT 0,
    quota_reset_at  TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- Payment Orders
-- ============================================================
CREATE TABLE orders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    plan_type       VARCHAR(20) NOT NULL,
    amount_cents    INT NOT NULL,
    status          VARCHAR(20) DEFAULT 'pending',
    wx_transaction_id VARCHAR(64),
    wx_prepay_id    VARCHAR(64),
    paid_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- ============================================================
-- Wrong Answer Book
-- ============================================================
CREATE TABLE wrong_answers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject         VARCHAR(100),
    question        TEXT NOT NULL,
    answer          TEXT,
    correct_answer  TEXT,
    tags            JSONB DEFAULT '[]',
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_wrong_answers_user ON wrong_answers(user_id);

-- ============================================================
-- Seed subscription plans
-- ============================================================
INSERT INTO subscription_plans (plan_type, name, price_cents, duration_days, daily_quota, features) VALUES
    ('daily', '包天', 990, 1, 1, '["单次资料整理", "PDF 导出 1 次"]'),
    ('monthly', '包月', 4900, 30, 10, '["不限次数整理", "不限次导出", "多格式支持"]'),
    ('quarterly', '包季度', 9900, 90, 10, '["不限次数整理", "不限次导出", "多格式支持", "错题本", "进度追踪"]')
ON CONFLICT (plan_type) DO NOTHING;
