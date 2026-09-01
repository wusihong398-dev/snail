# DEPLOYMENT.md

# 部署与回滚

## 部署前备份
```bash
STAMP="$(date +%Y%m%d_%H%M%S)"
mkdir -p /data/snail-chat-elf-backups

tar --exclude='snail-chat-elf/frontend/node_modules' --exclude='snail-chat-elf/frontend/.next' --exclude='snail-chat-elf/backend/venv' -zcf "/data/snail-chat-elf-backups/snail-chat-elf_${STAMP}.tar.gz" -C /data snail-chat-elf

sudo -u postgres pg_dump -Fc snail_chat > "/data/snail-chat-elf-backups/snail_chat_${STAMP}.dump"
```

## 数据库
`020_commercial_platform.sql` 已上线，禁止修改。
后续使用 `021_*.sql`, `022_*.sql`。

执行迁移前人工审查：
```bash
sudo -u postgres psql snail_chat -v ON_ERROR_STOP=1 -f backend/migrations/021_xxx.sql
```

## 后端
```bash
cd /data/snail-chat-elf/backend
source venv/bin/activate
python -m compileall -q app
python -c "from app.main import app; print(app.version)"
systemctl restart snail-api
sleep 3
systemctl status snail-api --no-pager
```

## 前端
```bash
cd /data/snail-chat-elf/frontend
npm run build
pm2 restart snail-admin
pm2 status
```

## 公网验收
```bash
curl -s https://jeyav.cn/api/health
curl -I https://jeyav.cn/admin
```

## 回滚
先 `ls -lht /data/snail-chat-elf-backups/` 确认版本和时间。
数据库恢复属于高风险动作，只有代码版本、数据库版本、备份时间一致时才执行 `pg_restore --clean --if-exists`。
