# AGENTS.md

# 蜗牛群聊精灵 Codex 强制开发规则

进入仓库后先阅读：
`CODEX_HANDOFF.md`、`ARCHITECTURE.md`、`ROADMAP.md`、`TESTING.md`、`DEPLOYMENT.md`、`SECURITY.md`、`.codex/tasks/NEXT_TASK.md`。

## 强制规则
- 当前生产版本：v0.3.0 商业化基础版。
- 增量开发，禁止推倒重写正常模块。
- 禁止清空/删除用户、订单、流水、恋爱、婚姻、宝宝、代理商、客户、授权码和兑换记录。
- 保留 `users.coins/member_level/member_started_at/member_expire_at` 兼容字段。
- `paid_diamonds` 与 `bonus_diamonds` 永久分账。
- 群管理员只能赠送蜗币和奖励钻石，不能生成付费钻石。
- 会员过期不得删除伴侣、强制离婚或删除宝宝，只限制继续新增。
- 群权限必须按 `customer_id + group_id + user_id` 隔离。
- 授权码不得保存完整明文，只保存前缀和安全哈希。
- 已上线 `020_commercial_platform.sql` 禁止修改；新迁移从 `021_*.sql` 开始。
- 授权库存、钻石额度、资产、佣金等关键余额变化必须有流水。
- 正式微信机器人兑换入口必须增加 API Secret/HMAC 等服务端签名。
- 禁止把管理员密码、JWT、数据库密码、机器人 Secret 写入源码。
- 大改前备份代码和 PostgreSQL。

## 每次修改后
后端：
```bash
cd /data/snail-chat-elf/backend
source venv/bin/activate
python -m compileall -q app
python -c "from app.main import app; print('FastAPI import OK', app.version)"
```

前端：
```bash
cd /data/snail-chat-elf/frontend
npm run build
```

部署：
```bash
systemctl restart snail-api
pm2 restart snail-admin
curl -s https://jeyav.cn/api/health
```

构建或测试失败时不得声称任务完成。
