# Stage B.1 production-dump migration rehearsal

Date: 2026-09-01 UTC

Status: **BLOCKED — acceptance not reached; do not run 021 in production.**

No command connected to or changed production `snail_chat`. Production source,
services, backups and migration 020 were not modified. No deployment, service
restart, commit or push occurred. Only the development copy and `/tmp` changed.

## 1. Dump and PostgreSQL information

The latest PostgreSQL dump found under `/data/snail-chat-elf-backups` is:

- Path: `/data/snail-chat-elf-backups/stage-b-20260901-nnFIeF/snail_chat_pre_stage_b.dump`
- Size: 214,320 bytes
- Modified: 2026-09-01 17:07:14.379787980 UTC
- SHA256: `f80d0607cafeba0b4e76005206d61bc8c3bef85fbed269621218939e9ef8b492`
- Custom archive 1.15, gzip, 305 TOC entries; `pg_restore -l` passed
- Dumped from/by PostgreSQL 16.15; installed tools are PostgreSQL 16.15
- Data-only extraction SHA256: `3fcfd40cced1d3e466d0b7aa69253740da51a68cc8c0d4ff471c748ecd2eb259`

The next newest dump is the 15:51 UTC production baseline; therefore the 17:07
dump is the latest available dump.

## 2. Rehearsal cluster/database/port

Required target: `/tmp` PostgreSQL 16 cluster, database
`snail_stageb_rehearsal_20260901`, random non-production port.

Result: **not created**. PostgreSQL refuses `initdb` as root, while the managed
sandbox rejects normal UID/GID changes: `chown` returns `Invalid argument`,
`runuser` returns `cannot set groups: Operation not permitted`, and `setpriv`
returns `setresuid failed: Invalid argument`. Network binding is enabled, but it
does not enable identity changes. No sandbox bypass, patched binary, container
daemon or existing PostgreSQL instance was used. Port 58991 was only an unbound,
fail-closed test URL, not a running database.

## 3. Pre-migration statistics

Counts and deterministic hashes below come from the dump's exact `COPY`
payloads; they are not database-side query results.

| Table | Rows | Payload SHA256 |
| --- | ---: | --- |
| users | 3 | `06b07275c3efb381bb45a8f65cd6aaf0cf96cbed82fb1004a219152c67f0c771` |
| agents | 1 | `7cb694400298fbc8b9b0cd6064dfc0b4caabe54ba53bb9304eabc36a34f126e1` |
| customers | 1 | `84bffb48fed45ebc6bcf821a4b37890807b92a143dbde50ff3f14acd5919aa5b` |
| groups | 2 | `16137a09c3df2953f9ff7ec4e680728f4dfff36269696076ac3e088ef57c8cb4` |
| customer_group_ownerships | 1 | `1355f68519baff4634db9faf4ebb591c3a69217867f9ca9374f0f098583c6a16` |
| group_members | 1 | `314d74dc7684a1eb7b64bbc4f63dca8ca0397ff078b356e7375a55a55202f90e` |
| redeem_codes | 2 | `bf8b00250aa2a052f272a35f7c72b996e5046ec8a6438d040d294f668abace00` |
| redeem_code_usages | 2 | `2bab8ded1aaa1c490fa652672013f78ea1db926a1f9ffc3edb5a661f5173ab53` |
| diamond_transactions | 1 | `5edba0d40fa40459e973a3a40d4a59ebca801be3c502c4b4ae81ceef6ffabfee` |
| agent_license_transactions | 0 | `01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b` |
| admin_asset_grants | 0 | `01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b` |
| shop_orders | 4 | `17e8a7cecb4f9ab32b6f840a2ae18e0ca0e2458a78f0676ec7b9e3b73109bea5` |
| coin_transactions | 4 | `a5ec33b429a46e6035fb55ae77ef7c4213b26f4c7dc8041380d59b52f1ad82bf` |
| user_relationships | 1 | `5dbb55fb037b6949557cb0a873f406dff7ba757c143d4ca9910b2549b3a4239a` |
| babies | 1 | `60c95ecc0bdc120dff0f37fb1dbd7d2ba988fa1615265cb8fba4ef30cb99b02e` |

Aggregates: user coins 1,560; paid diamonds 100; bonus diamonds 0; agent
license balance 9; agent diamond quota 9,900; diamond transaction amount 100;
coin transaction amount -2,240; redeem-code value 465, max-use sum 2 and
used-count sum 2.

## 4. Pre-migration anomaly checks

- negative user paid/bonus diamond balances: 0
- negative agent license/quota balances: 0
- invalid code value/counters: 0
- duplicate group ownership by `group_id`: 0
- active diamond codes: 0
- active multi-use diamond codes: 0

Database catalog, FK, sequence and constraint queries remain pending.

## 5. 021 result, post-migration statistics and consistency

021 was **not executed**. There is no restore time, migration duration,
transaction result, server log or rollback-on-error proof. Consequently there
are no post-migration statistics or valid pre/post equality claims, including
for historical balances, authorization relations and financial ledgers.

Static review found no executable `UPDATE`, `DELETE`, `DROP` or `TRUNCATE`.
020 remains unchanged (SHA256
`98b9a6f34f1932a9cd28428c8efa196d5dfca12f6a49e47460b8dd267677f8c2`).
Current 021 SHA256 is
`c9e55d70e3add0f142b03893b302ff4cbca10e31185490afd97cb80757c294e8`.
Static intent is not execution evidence.

## 6. New structure checks still required

- Tables `agent_diamond_quota_transactions`, `commercial_operation_logs`.
- Actor/idempotency fields on license transactions; reservation/request/result
  fields on codes and usages.
- Supporting and unique indexes, including one ownership per group and one
  `code_release` per redeem code.
- Nonnegative balance, code-bound, reservation-consistency, positive-ordinal
  and quota-arithmetic CHECK constraints.
- `snail_admin` owners/sequences and application privileges.

## 7. Python and pytest

- `python3 -m py_compile` for every changed Python file: passed.
- `python3 -m compileall -q backend/app backend/tests`: passed.
- FastAPI import with a non-production URL: passed, version 0.3.0.
- `git diff --check`: passed.
- pytest 9.1.1 was installed only under `/tmp`.

Full, asset and concurrency suites were invoked using the fixture's guarded
localhost/non-5432/`snail_stageb_test` URL. All cases stopped in `asyncSetUp`
with `ConnectionRefusedError`; these are environment setup failures, not failed
application assertions and not passes:

- complete: 25 setup failures, 5 warnings;
- commercial assets: 17 setup failures, 5 warnings;
- commercial concurrency: 8 setup failures, 5 warnings.

## 8. freeze / void / refund rule

The development copy now implements the approved policy incrementally:

- freeze and void each write an operation log and release no quota;
- refund is separate and explicit, requiring reason and idempotency key;
- only confirmed `agent_quota` reservation is eligible;
- refund equals `reserved_total - value * used_count`;
- legacy `reserved_total=NULL` and platform-manual codes are rejected;
- a partial unique index permits at most one release ledger per code;
- balance ledger and operation log commit atomically.

Tests cover a five-use 100-diamond code used once: reserve 500; freeze returns
0; void returns 0; explicit refund returns 400; replay returns no additional
quota; final quota is 900. The scenario could not execute without PostgreSQL,
so it is not marked passed.

## 9. Historical-data risk and rollback

- Legacy reservation provenance stays NULL and must never auto-refund.
- 021 aborts rather than correcting duplicates, negative balances or invalid
  counters.
- Old license actor fields remain NULL; no historical ledger is fabricated.
- Commission agents require funded quota for new diamond codes.
- Old application code after new ledger writes could re-enable unsafe issuance;
  prevent old issuance and prefer roll-forward.

Before production, take fresh matching code/database backups and hashes. A
failed 021 should roll back atomically, but rehearsal must prove it. After new
ledger writes, do not drop audit tables or fabricate reversals; prefer a forward
fix. Full dump restore is disaster recovery only and requires explicit approval.

## 10. Production recommendation and maintenance

**Do not approve 021 for production.** Missing evidence: exact dump restore,
exact migration execution, catalog checks, post-migration fingerprints, valid
pytest/asset/concurrency runs, and executed freeze/void/refund scenarios.

Once a non-root disposable PostgreSQL endpoint is available: repeat B.1; take
fresh production backups; enable maintenance mode for issuance/redemption;
apply the rehearsed 021 once with `ON_ERROR_STOP`; verify invariants; deploy the
matching backend; smoke test; reopen and monitor. Estimated window remains
20–30 minutes and must be revised using successful rehearsal timings.

## 11. Git status, diff stat and complete file list

Tracked diff stat:

```text
backend/app/models/commercial.py  |   8 +-
backend/app/routers/commercial.py | 227 ++++++++++++++++++++++++++++++++------
backend/app/schemas/commercial.py |  32 ++++--
backend/app/services/diamonds.py  |  13 +++
4 files changed, 234 insertions(+), 46 deletions(-)
```

Status and complete modified/untracked file list:

```text
 M backend/app/models/commercial.py
 M backend/app/routers/commercial.py
 M backend/app/schemas/commercial.py
 M backend/app/services/diamonds.py
?? STAGE_B_MIGRATION_REHEARSAL.md
?? STAGE_B_MIGRATION_REHEARSAL.partial_20260902.md
?? STAGE_B_REVIEW.md
?? backend/app/models/commercial_operations.py
?? backend/app/services/commercial_operations.py
?? backend/migrations/021_commercial_operations.sql
?? backend/requirements-dev.txt
?? backend/tests/__init__.py
?? backend/tests/conftest.py
?? backend/tests/support.py
?? backend/tests/test_commercial_assets.py
?? backend/tests/test_commercial_concurrency.py
```

No commit or push was performed.
