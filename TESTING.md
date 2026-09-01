# TESTING.md

# 测试标准

## 后端
```bash
cd /data/snail-chat-elf/backend
source venv/bin/activate
python -m compileall -q app
python -c "from app.main import app; print('FastAPI import OK / version:', app.version)"
```

## 前端
```bash
cd /data/snail-chat-elf/frontend
npm run build
```

## 服务
```bash
systemctl status snail-api --no-pager
pm2 status
curl -s https://jeyav.cn/api/health
```

## 旧功能回归
```bash
curl -s https://jeyav.cn/api/users
curl -s https://jeyav.cn/api/relationships
curl -s https://jeyav.cn/api/babies
curl -s https://jeyav.cn/api/shop/products
```

## 商业 API
使用新登录取得的管理员 Bearer Token，检查：
- `/api/commercial/agents`
- `/api/commercial/customers`
- `/api/commercial/code-usages`
- `/api/commercial/diamond-transactions`

## 群授权码验收
- prepaid/hybrid 生成后库存减少。
- 首次兑换成功。
- Customer/Ownership/GroupMember 正确。
- role=owner。
- 使用时间正确。
- 重复兑换失败。
- 已绑定其他客户的群不能被抢占。

## 钻石码验收
- 生成100钻石码后 `diamond_quota -100`。
- 兑换后 `paid_diamonds +100`。
- `bonus_diamonds` 不变。
- 钻石流水和兑换记录都写入。
- 重复兑换失败。

## 权限
必须验证跨代理、跨客户、跨群访问被拒绝；普通成员不能赠资产；群管理员不能增加付费钻石。

## 前端显示全0
先重新登录、Ctrl+F5、检查 `localStorage.getItem("token")` 和 Network 401，不能误判数据库丢失。
