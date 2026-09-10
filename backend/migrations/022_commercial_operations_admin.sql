-- Stage C: additive admin-operation idempotency. REVIEW ONLY; do not run in production.
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';

ALTER TABLE commercial_operation_logs ADD COLUMN request_id VARCHAR(128);
CREATE UNIQUE INDEX uq_commercial_operation_request
    ON commercial_operation_logs(operation_type, target_type, target_id, request_id)
    WHERE request_id IS NOT NULL;

COMMIT;
