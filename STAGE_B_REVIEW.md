# Stage B — commercial asset safety (not deployed)

Development branch: `commercial-asset-safety-v0.3.1`, based on
`dc4230bf65adae6b0c1c89e13389ca3b8e5adc7b`. No commit/push is authorized.
Production source, secrets, services and database are not switched.

## Backup and production read-only preflight

New private directory: `/data/snail-chat-elf-backups/stage-b-20260901-nnFIeF`.

| File | Bytes | SHA256 |
| --- | ---: | --- |
| snail-chat-elf-pre-stage-b.tar.gz | 596916562 | 258e9741832afae7305dfa6aff77729eaf9efc70a9b2649399761f5ee746f8b4 |
| snail_chat_pre_stage_b.dump | 214320 | f80d0607cafeba0b4e76005206d61bc8c3bef85fbed269621218939e9ef8b492 |

Archive integrity and dump directory readability verified; not a restore drill.
At preflight: active diamond codes 0; active multi-use diamond codes 0;
negative agent/user diamond balances 0; duplicate group ownerships 0;
invalid code counters 0. Repeat before any approved production migration.

## Changes and transaction contract

- New agent balances start at zero and get real `initial` ledger entries.
  No historical agent gets a synthesized initial transaction.
- All agent modes reserve `value * max_uses` for new agent diamond codes.
  Insufficient quota/overflow rejects the transaction. Group licenses retain
  one inventory unit per customer license for prepaid/hybrid agents.
- The sole agent mutation service writes before/amount/after, actor, reason,
  code reference and idempotency key. Helpers flush but NEVER commit.
- Existing router request transactions commit once after all writes; failures
  roll back on session closure (`get_db`). Service callers must roll back on
  any exception, not catch an exception and then commit a partial transaction.
- User diamond functions retain the original split-ledger implementation,
  add row locks/fresh reads, and preserve bonus-first consumption.
- Commercial asset grants also record authenticated admin identity, validate
  customer/group/member scope, and append a coin ledger for coin grants.
  This is not a replacement for future per-permission group authorization.

## Lock order

Generation request guard (when supplied) -> agent -> redeem_code -> user ->
customer -> group. A missing user/group takes a namespaced advisory transaction
lock immediately before that resource's row lock. Helpers may reacquire a row
already held by the same transaction; never acquire an earlier new resource.
The owner user lock serializes account-level group counts; customer/group locks
and a unique group ownership index prevent concurrent group claims.

## Idempotency and API compatibility

- `request_id` is optional for creation and legacy single-use redemption.
- Creation uses authenticated admin + request_id. A retry receives 409; full
  plaintext codes are NEVER saved/re-shown, even for a timed-out creation.
- Multi-use redemption REQUIRES a stable request_id (bot/message identifier).
- Redemption key: code_id + request_id. A committed successful retry returns
  stored result; reuse for another wx user/group returns 409. Another request
  against a used single-use code is rejected. A new request_id on a multi-use
  code means a genuinely new use, not a retry.
- A second unique code_id + use_number index protects committed use ordinals.
- Failure writes no partial credit/usage/ledger. Failed attempts are not
  persisted in this stage; separate security failure auditing remains future work.
- New read-only `/commercial/codes/{code_id}/reservation` requires admin login.

## Migration

Full SQL: `backend/migrations/021_commercial_operations.sql` (020 unchanged).
Adds quota ledger, three license audit fields, operation logs, code reservation
and request fields, usage idempotency/result fields, indexes and constraints.
No UPDATE/DELETE/DROP, no historical backfill. Old audit fields remain NULL.
Unknown legacy reservation is NULL, never claimed to be zero or fully reserved.
Nonnegative/counter constraints are validated; duplicates/invalid legacy data
abort the entire migration without correction. Lock timeout 5s, statement
timeout 60s. This is a numbered one-time migration, not a rerunnable upgrade.

No production execution has occurred. In isolated tests, the unchanged 020 and
full 021 run on synthetic data in a disposable PostgreSQL 16 cluster, including
an old-row preservation test. Apply only after a fresh preflight and approval.
After real new ledger rows exist, do NOT drop audit tables for rollback.
Prefer roll-forward; any code rollback must separately prevent old unsafe
issuance. Backup restore is not an automatic rollback policy.

## Business decisions still required

- Freeze: recommend blocking new uses without releasing reservation.
- Void: recommend a later explicit, idempotent, audited release of only unused
  confirmed agent reservation; never refund used diamonds.
- Partial use: confirmed remaining = reserved_total - value * used_count.
- Legacy codes: reservation is unknown; reconcile manually, no automatic debit.
- Platform (agent_id NULL) issuance preserves existing admin-only behavior and
  is logged as `platform_manual`; there is NO fabricated agent quota reserve.
  reserved_total/remaining_reserved remain NULL. Decide separately whether
  platform issuance must require a funded agent or a platform funding ledger.
- Commission agents now require diamond quota too, per the stage requirements;
  confirm operational funding before production launch.
- No release/refund endpoint is exposed; service rejects `code_release` until
  the commercial policy is approved. Frozen/void codes already fail redemption.

## Verification

Tests: `backend/tests/test_commercial_assets.py` and
`backend/tests/test_commercial_concurrency.py`, plus shared guarded fixtures.
24 tests pass on real isolated PostgreSQL; 5 pre-existing Pydantic Config
deprecation warnings. Initial fixture schema-USAGE failure was corrected;
no checks were skipped. No frontend files changed, so frontend build omitted.

Use a separate test environment with `requirements-dev.txt` and set
`TEST_DATABASE_URL` to a disposable local PostgreSQL database named exactly
`snail_stageb_test`, on a non-5432 port, then run:

```sh
python -m pytest -q tests -p no:cacheprovider --tb=short
```

Fixtures reject production-like targets, create synthetic schemas, run 020/021,
and drop ONLY their own test schemas. Never point them at production.
Production 021, production write regressions, service restarts and deployment
remain explicitly pending user approval.
