-- Seed subscription plans data
-- Run: psql -U postgres -d study_assistant -f scripts/seed_subscription_plans.sql

INSERT INTO subscription_plans (plan_type, name, price_cents, duration_days, daily_quota, features) VALUES
    ('daily', '包天', 990, 1, 1, '["单次资料整理", "PDF 导出 1 次"]'),
    ('monthly', '包月', 4900, 30, 10, '["不限次数整理", "不限次导出", "多格式支持"]'),
    ('quarterly', '包季度', 9900, 90, 10, '["不限次数整理", "不限次导出", "多格式支持", "错题本", "进度追踪"]')
ON CONFLICT (plan_type) DO UPDATE SET
    price_cents = EXCLUDED.price_cents,
    duration_days = EXCLUDED.duration_days,
    daily_quota = EXCLUDED.daily_quota,
    features = EXCLUDED.features;
