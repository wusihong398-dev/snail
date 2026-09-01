BEGIN;

ALTER TABLE users ADD COLUMN IF NOT EXISTS paid_diamonds INTEGER NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS bonus_diamonds INTEGER NOT NULL DEFAULT 0;

ALTER TABLE groups ADD COLUMN IF NOT EXISTS customer_id INTEGER;

CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    agent_code VARCHAR(64) NOT NULL UNIQUE,
    agent_type VARCHAR(30) NOT NULL DEFAULT 'commission',
    commission_rate NUMERIC(8,4) NOT NULL DEFAULT 0,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    parent_agent_id INTEGER,
    license_balance INTEGER NOT NULL DEFAULT 0,
    diamond_quota INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER,
    owner_user_id INTEGER NOT NULL,
    name VARCHAR(128),
    plan_code VARCHAR(64) NOT NULL DEFAULT 'basic',
    license_status VARCHAR(30) NOT NULL DEFAULT 'active',
    license_started_at TIMESTAMPTZ,
    license_expire_at TIMESTAMPTZ,
    max_groups INTEGER NOT NULL DEFAULT 3,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_customers_agent_id ON customers(agent_id);
CREATE INDEX IF NOT EXISTS ix_customers_owner_user_id ON customers(owner_user_id);

CREATE TABLE IF NOT EXISTS customer_group_ownerships (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    owner_user_id INTEGER NOT NULL,
    agent_id INTEGER,
    source_code_id INTEGER,
    activated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(customer_id, group_id)
);
CREATE INDEX IF NOT EXISTS ix_customer_group_ownership_group ON customer_group_ownerships(group_id);

CREATE TABLE IF NOT EXISTS group_members (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    group_nickname VARCHAR(128),
    member_role VARCHAR(30) NOT NULL DEFAULT 'member',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(group_id, user_id)
);
CREATE INDEX IF NOT EXISTS ix_group_members_user ON group_members(user_id);
CREATE INDEX IF NOT EXISTS ix_group_members_customer ON group_members(customer_id);

CREATE TABLE IF NOT EXISTS group_admin_permissions (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    permission_key VARCHAR(80) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    granted_by_user_id INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(group_id, user_id, permission_key)
);

CREATE TABLE IF NOT EXISTS diamond_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    diamond_type VARCHAR(20) NOT NULL,
    amount INTEGER NOT NULL,
    paid_before INTEGER NOT NULL DEFAULT 0,
    paid_after INTEGER NOT NULL DEFAULT 0,
    bonus_before INTEGER NOT NULL DEFAULT 0,
    bonus_after INTEGER NOT NULL DEFAULT 0,
    order_id INTEGER,
    reference_type VARCHAR(50),
    reference_id INTEGER,
    description VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT diamond_type_check CHECK (diamond_type IN ('paid','bonus','mixed'))
);
CREATE INDEX IF NOT EXISTS ix_diamond_transactions_user ON diamond_transactions(user_id);
CREATE INDEX IF NOT EXISTS ix_diamond_transactions_created ON diamond_transactions(created_at);

CREATE TABLE IF NOT EXISTS user_entitlements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    entitlement_key VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    scope_type VARCHAR(30) NOT NULL DEFAULT 'global',
    scope_id INTEGER,
    source_type VARCHAR(30) NOT NULL DEFAULT 'purchase',
    source_id INTEGER,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, entitlement_key, scope_type, scope_id)
);
CREATE INDEX IF NOT EXISTS ix_user_entitlements_user ON user_entitlements(user_id);

CREATE TABLE IF NOT EXISTS redeem_codes (
    id SERIAL PRIMARY KEY,
    code_prefix VARCHAR(32) NOT NULL,
    code_hash VARCHAR(128) NOT NULL UNIQUE,
    code_type VARCHAR(40) NOT NULL,
    agent_id INTEGER,
    customer_id INTEGER,
    product_id INTEGER,
    value INTEGER NOT NULL DEFAULT 0,
    metadata_json TEXT,
    valid_from TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    max_uses INTEGER NOT NULL DEFAULT 1,
    used_count INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    created_by VARCHAR(80),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_redeem_codes_agent ON redeem_codes(agent_id);
CREATE INDEX IF NOT EXISTS ix_redeem_codes_type ON redeem_codes(code_type);
CREATE INDEX IF NOT EXISTS ix_redeem_codes_status ON redeem_codes(status);

CREATE TABLE IF NOT EXISTS redeem_code_usages (
    id SERIAL PRIMARY KEY,
    code_id INTEGER NOT NULL,
    agent_id INTEGER,
    customer_id INTEGER,
    user_id INTEGER,
    wx_user_id VARCHAR(128),
    group_id INTEGER,
    wx_group_id VARCHAR(128),
    usage_type VARCHAR(40) NOT NULL,
    value INTEGER NOT NULL DEFAULT 0,
    success BOOLEAN NOT NULL DEFAULT FALSE,
    failure_reason VARCHAR(255),
    used_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_redeem_code_usages_code ON redeem_code_usages(code_id);
CREATE INDEX IF NOT EXISTS ix_redeem_code_usages_agent ON redeem_code_usages(agent_id);
CREATE INDEX IF NOT EXISTS ix_redeem_code_usages_used_at ON redeem_code_usages(used_at);

CREATE TABLE IF NOT EXISTS admin_asset_grants (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER,
    customer_id INTEGER NOT NULL,
    group_id INTEGER,
    operator_user_id INTEGER NOT NULL,
    target_user_id INTEGER NOT NULL,
    asset_type VARCHAR(40) NOT NULL,
    amount INTEGER NOT NULL,
    balance_before INTEGER NOT NULL DEFAULT 0,
    balance_after INTEGER NOT NULL DEFAULT 0,
    reason VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_admin_asset_grants_customer ON admin_asset_grants(customer_id);
CREATE INDEX IF NOT EXISTS ix_admin_asset_grants_target ON admin_asset_grants(target_user_id);

INSERT INTO system_settings(setting_key,setting_value,value_type,title,description)
VALUES
('wechat_max_groups_per_account','20','integer','单微信号最大群数量','平台风控上限，可根据微信风控情况动态调整'),
('admin_code_default_hours','168','integer','管理授权码默认有效小时','代理商生成群管理授权码后的默认有效期'),
('diamond_code_default_hours','720','integer','钻石兑换码默认有效小时','代理商生成钻石兑换码后的默认有效期'),
('partner_slot_diamond_price','500','integer','额外伴侣槽钻石价格','永久增加1个伴侣名额所需钻石'),
('baby_slot_diamond_price','200','integer','额外宝宝槽钻石价格','永久增加1个宝宝名额所需钻石'),
('max_extra_partner_slots','3','integer','最大额外伴侣槽','每个用户最多永久增购的伴侣槽数量'),
('max_extra_baby_slots','6','integer','最大额外宝宝槽','每个用户最多永久增购的宝宝槽数量')
ON CONFLICT (setting_key) DO NOTHING;

CREATE TABLE IF NOT EXISTS agent_commissions (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER NOT NULL,
    customer_id INTEGER,
    order_no VARCHAR(80),
    order_amount_cents INTEGER NOT NULL DEFAULT 0,
    commission_rate NUMERIC(8,4) NOT NULL DEFAULT 0,
    commission_amount_cents INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    settled_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ix_agent_commissions_agent ON agent_commissions(agent_id);

CREATE TABLE IF NOT EXISTS agent_license_transactions (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER NOT NULL,
    transaction_type VARCHAR(40) NOT NULL,
    amount INTEGER NOT NULL,
    balance_before INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    reference_type VARCHAR(40),
    reference_id INTEGER,
    description VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_agent_license_transactions_agent ON agent_license_transactions(agent_id);

CREATE TABLE IF NOT EXISTS group_admin_sessions (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    token_hash VARCHAR(128) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_group_admin_sessions_user ON group_admin_sessions(user_id);

CREATE TABLE IF NOT EXISTS membership_plans (
    id SERIAL PRIMARY KEY,
    code VARCHAR(40) NOT NULL UNIQUE,
    name VARCHAR(80) NOT NULL,
    member_level VARCHAR(30) NOT NULL DEFAULT 'normal',
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS membership_plan_entitlements (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL,
    entitlement_key VARCHAR(100) NOT NULL,
    entitlement_value VARCHAR(100) NOT NULL,
    UNIQUE(plan_id, entitlement_key)
);

CREATE TABLE IF NOT EXISTS membership_products (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    duration_days INTEGER NOT NULL,
    price_cents INTEGER NOT NULL DEFAULT 0,
    diamond_price INTEGER NOT NULL DEFAULT 0,
    bonus_diamonds INTEGER NOT NULL DEFAULT 0,
    bonus_grant_mode VARCHAR(20) NOT NULL DEFAULT 'immediate',
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_memberships (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    plan_id INTEGER NOT NULL,
    product_id INTEGER,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    next_bonus_at TIMESTAMPTZ,
    source_type VARCHAR(30) NOT NULL DEFAULT 'purchase',
    source_id INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_user_memberships_user ON user_memberships(user_id);

INSERT INTO membership_plans(code,name,member_level,sort_order) VALUES
('normal','普通用户','normal',0),
('vip','VIP','vip',10),
('svip','SVIP','svip',20)
ON CONFLICT (code) DO NOTHING;

INSERT INTO membership_plan_entitlements(plan_id,entitlement_key,entitlement_value)
SELECT id,'max_partners','1' FROM membership_plans WHERE code='normal'
ON CONFLICT (plan_id,entitlement_key) DO NOTHING;
INSERT INTO membership_plan_entitlements(plan_id,entitlement_key,entitlement_value)
SELECT id,'max_children_per_couple','1' FROM membership_plans WHERE code='normal'
ON CONFLICT (plan_id,entitlement_key) DO NOTHING;
INSERT INTO membership_plan_entitlements(plan_id,entitlement_key,entitlement_value)
SELECT id,'max_children_total','1' FROM membership_plans WHERE code='normal'
ON CONFLICT (plan_id,entitlement_key) DO NOTHING;

INSERT INTO membership_plan_entitlements(plan_id,entitlement_key,entitlement_value)
SELECT id,'max_partners','2' FROM membership_plans WHERE code='vip'
ON CONFLICT (plan_id,entitlement_key) DO NOTHING;
INSERT INTO membership_plan_entitlements(plan_id,entitlement_key,entitlement_value)
SELECT id,'max_children_per_couple','2' FROM membership_plans WHERE code='vip'
ON CONFLICT (plan_id,entitlement_key) DO NOTHING;
INSERT INTO membership_plan_entitlements(plan_id,entitlement_key,entitlement_value)
SELECT id,'max_children_total','4' FROM membership_plans WHERE code='vip'
ON CONFLICT (plan_id,entitlement_key) DO NOTHING;

INSERT INTO membership_plan_entitlements(plan_id,entitlement_key,entitlement_value)
SELECT id,'max_partners','3' FROM membership_plans WHERE code='svip'
ON CONFLICT (plan_id,entitlement_key) DO NOTHING;
INSERT INTO membership_plan_entitlements(plan_id,entitlement_key,entitlement_value)
SELECT id,'max_children_per_couple','3' FROM membership_plans WHERE code='svip'
ON CONFLICT (plan_id,entitlement_key) DO NOTHING;
INSERT INTO membership_plan_entitlements(plan_id,entitlement_key,entitlement_value)
SELECT id,'max_children_total','6' FROM membership_plans WHERE code='svip'
ON CONFLICT (plan_id,entitlement_key) DO NOTHING;

-- 运行服务使用 snail_admin，统一修正新对象所有权和权限
ALTER TABLE agents OWNER TO snail_admin;
ALTER TABLE customers OWNER TO snail_admin;
ALTER TABLE customer_group_ownerships OWNER TO snail_admin;
ALTER TABLE group_members OWNER TO snail_admin;
ALTER TABLE group_admin_permissions OWNER TO snail_admin;
ALTER TABLE diamond_transactions OWNER TO snail_admin;
ALTER TABLE user_entitlements OWNER TO snail_admin;
ALTER TABLE redeem_codes OWNER TO snail_admin;
ALTER TABLE redeem_code_usages OWNER TO snail_admin;
ALTER TABLE admin_asset_grants OWNER TO snail_admin;
ALTER TABLE agent_commissions OWNER TO snail_admin;
ALTER TABLE agent_license_transactions OWNER TO snail_admin;
ALTER TABLE group_admin_sessions OWNER TO snail_admin;
ALTER TABLE membership_plans OWNER TO snail_admin;
ALTER TABLE membership_plan_entitlements OWNER TO snail_admin;
ALTER TABLE membership_products OWNER TO snail_admin;
ALTER TABLE user_memberships OWNER TO snail_admin;

ALTER SEQUENCE agents_id_seq OWNER TO snail_admin;
ALTER SEQUENCE customers_id_seq OWNER TO snail_admin;
ALTER SEQUENCE customer_group_ownerships_id_seq OWNER TO snail_admin;
ALTER SEQUENCE group_members_id_seq OWNER TO snail_admin;
ALTER SEQUENCE group_admin_permissions_id_seq OWNER TO snail_admin;
ALTER SEQUENCE diamond_transactions_id_seq OWNER TO snail_admin;
ALTER SEQUENCE user_entitlements_id_seq OWNER TO snail_admin;
ALTER SEQUENCE redeem_codes_id_seq OWNER TO snail_admin;
ALTER SEQUENCE redeem_code_usages_id_seq OWNER TO snail_admin;
ALTER SEQUENCE admin_asset_grants_id_seq OWNER TO snail_admin;
ALTER SEQUENCE agent_commissions_id_seq OWNER TO snail_admin;
ALTER SEQUENCE agent_license_transactions_id_seq OWNER TO snail_admin;
ALTER SEQUENCE group_admin_sessions_id_seq OWNER TO snail_admin;
ALTER SEQUENCE membership_plans_id_seq OWNER TO snail_admin;
ALTER SEQUENCE membership_plan_entitlements_id_seq OWNER TO snail_admin;
ALTER SEQUENCE membership_products_id_seq OWNER TO snail_admin;
ALTER SEQUENCE user_memberships_id_seq OWNER TO snail_admin;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO snail_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO snail_admin;

COMMIT;
