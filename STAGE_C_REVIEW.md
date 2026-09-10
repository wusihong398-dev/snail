# Stage C.1 数据库集成验收 — 商业运营后台 v0.3.2

日期：2026-09-10 UTC（本轮重新验收）  
分支：`commercial-operations-v0.3.2`  
状态：业务与数据库结构验收通过；生产角色原样迁移验收仍有环境 BLOCKER，未执行生产迁移。

## 安全边界与连接验证

- 唯一测试 URL：`postgresql+asyncpg://snail_test:***@127.0.0.1:58991/snail_stageb_test`。
- 服务端查询返回：host `127.0.0.1`、port `58991`、database `snail_stageb_test`、user `snail_test`、PostgreSQL `16.15`。
- 未连接 `snail_chat`，未连接 5432，未修改 `/data/snail-chat-elf` 生产源码。
- 未执行生产 021/022，未重启服务，未部署、commit 或 push。
- 清理范围仅为测试库中的 `stageb_*` 与 `stagec_acceptance` schema。
- 本轮服务端再次确认 PostgreSQL `16.15`；`snail_test` 不是 superuser、无
  `CREATEROLE`，实例仍不存在 `snail_admin`。
- 测试依赖仅安装到 `/tmp/snail-stagec-pydeps`；未修改生产虚拟环境。

## 020 → 021 → 022 与结构结果

专用实例没有迁移固定引用的 `snail_admin` 角色，且 `snail_test` 不是 superuser、无 `CREATEROLE`。原始迁移首次执行在 `GRANT ... TO snail_admin` 前置处失败。创建角色属于实例级修改，超出“只修改 snail_stageb_test”的授权，因此未创建。

测试夹具随后仅在内存中把 020/021 的对象 owner/grantee `snail_admin` 映射为当前隔离登录 `snail_test`；020、021、022 文件本身未修改。映射后每个测试 schema 及固定 catalog 验收 schema 均真实执行 020 → 021 → 022，三段 transaction 均 COMMIT 成功。

Catalog 核验通过：

- 新表：`agent_diamond_quota_transactions`、`commercial_operation_logs`。
- 新字段：license transaction actor/idempotency；code request/reservation；usage request/ordinal/result；operation log request ID。
- 13 个目标索引全部存在，包括 creation/usage/admin-operation request-id 条件唯一索引、单群单客户唯一索引、单 code release 唯一索引。
- 10 个 CHECK 全部存在且 `convalidated=true`：代理/用户余额非负、code 使用边界、reservation 一致性、usage ordinal、quota before/after 与算术、transaction type、diamond type。
- request-id 幂等通过业务测试和数据库条件唯一索引双重验证。

严格结论：

- 角色映射后的 DDL transaction、结构及业务兼容：**PASS**。
- 包含生产 `snail_admin` ownership/grant 的原样 020 → 021 → 022：**FAIL / BLOCKED（测试实例缺角色且当前账号无权创建）**。

## pytest 验收结果

发现并修复两项测试验收代码问题：

- `backend/tests/support.py`：隔离实例缺生产角色时，仅为执行测试映射 owner/grantee，不修改迁移文件。
- `backend/tests/test_commercial_assets.py`：补齐遗漏的 `adjust_agent_diamond_quota` 导入。
- `backend/tests/test_commercial_admin.py`：增加会员商品新增/编辑/上下架幂等、授权库存流水及代理钻石额度流水分页筛选验证。

2026-09-10 本轮最终结果：

- 完整 pytest：**29 passed, 0 failed, 5 warnings**，16.12 秒。
- commercial assets：**17 passed, 0 failed**，8.60 秒。
- commercial concurrency 第 1 轮：**8 passed, 0 failed**，7.21 秒。
- commercial concurrency 第 2 轮：**8 passed, 0 failed**，7.08 秒。
- commercial concurrency 第 3 轮：**8 passed, 0 failed**，6.92 秒。
- commercial admin：**4 passed, 0 failed**，3.12 秒。

5 个 warning 均为已有 Pydantic class-based `Config` 弃用提示，不是测试失败。

覆盖并通过：多次钻石码全额预留、额度不足回滚、并发不超扣、request-id 幂等、paid/bonus 永久分账及 bonus 优先消费、freeze/unfreeze/void/refund、refund 后 unfreeze 拒绝、legacy `reserved_total=NULL` 禁止退款、客户续期/暂停/恢复、`max_groups` 下限、授权码/兑换记录/钻石流水分页结构、授权库存流水、代理钻石额度流水、会员商品运营。

## 最终静态检查与构建

- `git diff --check`：**PASS**。
- 所有 6 个修改 Python 文件 `python3 -m py_compile`：**PASS**。
- `python3 -m compileall -q backend/app backend/tests`：**PASS**。
- `frontend/npm run build`：**PASS**；Next.js 16.3.1 编译、TypeScript 检查及 17 个静态页面生成成功。
- 本轮未发现需要继续修改的代码；仅更新本验收记录。

## BLOCKER 与建议

仍存在一个环境 BLOCKER：该专用实例缺少 `snail_admin`，无法原样验收 production ownership/grant 语句。未发现 Stage C 业务代码或 021/022 表结构 blocker。

**建议 021/022 进入正式生产迁移演练，但不建议直接执行生产迁移。** 下一轮应使用含 `snail_admin`、权限模型与生产一致的隔离 PostgreSQL 16 环境，原样执行 020 → 021 → 022，并继续完成 Stage B production-dump 前后指纹验收；通过后再申请生产迁移批准。

## 最终报告摘要

- 测试数据库连接验证：**PASS**
- 020→021→022：**FAIL / BLOCKED（原样角色路径）；角色映射下 transaction/结构 PASS**
- 完整 pytest 测试总数：**29**
- passed：**29**
- failed：**0**
- commercial assets：**17 passed**
- commercial concurrency 第1轮：**8 passed**
- commercial concurrency 第2轮：**8 passed**
- commercial concurrency 第3轮：**8 passed**
- commercial admin：**4 passed**
- frontend build：**PASS**
- 是否仍存在 BLOCKER：**是，仅 production-role 原样迁移验收环境 blocker**
- 021/022 是否建议进入正式生产迁移演练：**是；不得跳过演练直接上生产**

最终 `git diff --stat` 与 `git status --short --branch` 见本次验收交付消息；未 commit、未 push。
