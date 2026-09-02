-- Stage B: additive migration. REVIEW ONLY until production approval.
-- No legacy balances/codes/usages are rewritten or fabricated.
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';

CREATE TABLE agent_diamond_quota_transactions (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER NOT NULL REFERENCES agents(id),
    transaction_type VARCHAR(40) NOT NULL CHECK (transaction_type IN
        ('initial','code_reserve','code_release','admin_adjustment','manual_grant','correction')),
    amount BIGINT NOT NULL,
    quota_before BIGINT NOT NULL CHECK (quota_before >= 0),
    quota_after BIGINT NOT NULL CHECK (quota_after >= 0),
    redeem_code_id INTEGER REFERENCES redeem_codes(id),
    customer_id INTEGER REFERENCES customers(id),
    operator_type VARCHAR(30) NOT NULL,
    operator_name VARCHAR(128) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    idempotency_key VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (quota_after = quota_before + amount)
);
CREATE UNIQUE INDEX uq_agent_quota_idempotency
    ON agent_diamond_quota_transactions(agent_id, idempotency_key)
    WHERE idempotency_key IS NOT NULL;
CREATE INDEX ix_agent_quota_created ON agent_diamond_quota_transactions(agent_id, created_at);
CREATE INDEX ix_agent_quota_code ON agent_diamond_quota_transactions(redeem_code_id);
CREATE UNIQUE INDEX uq_agent_quota_code_release
    ON agent_diamond_quota_transactions(redeem_code_id)
    WHERE transaction_type = 'code_release';

-- NULL for legacy rows: never invent their historical operator.
ALTER TABLE agent_license_transactions ADD COLUMN operator_type VARCHAR(30);
ALTER TABLE agent_license_transactions ADD COLUMN operator_name VARCHAR(128);
ALTER TABLE agent_license_transactions ADD COLUMN idempotency_key VARCHAR(128);
CREATE UNIQUE INDEX uq_agent_license_idempotency
    ON agent_license_transactions(agent_id, idempotency_key)
    WHERE idempotency_key IS NOT NULL;
CREATE INDEX ix_agent_license_created ON agent_license_transactions(agent_id, created_at);

CREATE TABLE commercial_operation_logs (
    id SERIAL PRIMARY KEY,
    operation_type VARCHAR(50) NOT NULL,
    operator_name VARCHAR(128) NOT NULL,
    target_type VARCHAR(40) NOT NULL,
    target_id INTEGER NOT NULL,
    details_json TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_commercial_operation_target ON commercial_operation_logs(target_type, target_id, created_at);

-- Legacy reservation is UNKNOWN, not zero and not a backfilled transaction.
ALTER TABLE redeem_codes ADD COLUMN request_id VARCHAR(128);
ALTER TABLE redeem_codes ADD COLUMN reservation_source VARCHAR(30);
ALTER TABLE redeem_codes ADD COLUMN reserved_total BIGINT;
CREATE UNIQUE INDEX uq_code_creation_request ON redeem_codes(created_by, request_id)
    WHERE request_id IS NOT NULL;
ALTER TABLE redeem_code_usages ADD COLUMN request_id VARCHAR(128);
ALTER TABLE redeem_code_usages ADD COLUMN use_number INTEGER;
ALTER TABLE redeem_code_usages ADD COLUMN result_json TEXT;
CREATE UNIQUE INDEX uq_code_usage_request ON redeem_code_usages(code_id, request_id)
    WHERE request_id IS NOT NULL;
CREATE UNIQUE INDEX uq_code_usage_number ON redeem_code_usages(code_id, use_number)
    WHERE use_number IS NOT NULL;
CREATE INDEX ix_code_usage_user_created ON redeem_code_usages(user_id, used_at);

-- A conflict aborts the whole migration. Never delete duplicates automatically.
CREATE UNIQUE INDEX uq_single_customer_per_group ON customer_group_ownerships(group_id);

-- Validate without correcting old data; on any invalid row the transaction aborts.
ALTER TABLE agents ADD CONSTRAINT ck_agent_balances_nonnegative
    CHECK (license_balance >= 0 AND diamond_quota >= 0) NOT VALID;
ALTER TABLE agents VALIDATE CONSTRAINT ck_agent_balances_nonnegative;
ALTER TABLE users ADD CONSTRAINT ck_user_diamonds_nonnegative
    CHECK (paid_diamonds >= 0 AND bonus_diamonds >= 0) NOT VALID;
ALTER TABLE users VALIDATE CONSTRAINT ck_user_diamonds_nonnegative;
ALTER TABLE redeem_codes ADD CONSTRAINT ck_code_usage_bounds
    CHECK (value >= 0 AND max_uses >= 1 AND used_count >= 0 AND used_count <= max_uses) NOT VALID;
ALTER TABLE redeem_codes VALIDATE CONSTRAINT ck_code_usage_bounds;
ALTER TABLE redeem_codes ADD CONSTRAINT ck_code_reservation
    CHECK (((reservation_source IS NULL AND reserved_total IS NULL)
        OR (reservation_source = 'platform_manual' AND reserved_total IS NULL)
        OR (reservation_source = 'agent_quota' AND agent_id IS NOT NULL
            AND reserved_total IS NOT NULL AND reserved_total = value::BIGINT * max_uses
            AND reserved_total >= 0)) IS TRUE) NOT VALID;
ALTER TABLE redeem_codes VALIDATE CONSTRAINT ck_code_reservation;
ALTER TABLE redeem_code_usages ADD CONSTRAINT ck_usage_number_positive
    CHECK (use_number IS NULL OR use_number > 0) NOT VALID;
ALTER TABLE redeem_code_usages VALIDATE CONSTRAINT ck_usage_number_positive;

ALTER TABLE agent_diamond_quota_transactions OWNER TO snail_admin;
ALTER SEQUENCE agent_diamond_quota_transactions_id_seq OWNER TO snail_admin;
ALTER TABLE commercial_operation_logs OWNER TO snail_admin;
ALTER SEQUENCE commercial_operation_logs_id_seq OWNER TO snail_admin;
COMMIT;
