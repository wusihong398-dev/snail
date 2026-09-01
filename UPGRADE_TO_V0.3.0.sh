#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-/data/snail-chat-elf}"
BACKUP_ROOT="${BACKUP_ROOT:-/data/snail-chat-elf-backups}"
STAMP="$(date +%Y%m%d_%H%M%S)"

if [ ! -d "$ROOT/backend" ] || [ ! -d "$ROOT/frontend" ]; then
  echo "错误：没有找到项目目录：$ROOT"
  exit 1
fi

mkdir -p "$BACKUP_ROOT"

echo "===== 1/7 备份当前代码 ====="
tar --exclude='frontend/node_modules' --exclude='frontend/.next' --exclude='backend/venv' \
  -czf "$BACKUP_ROOT/snail-chat-elf-before-v030_${STAMP}.tar.gz" -C "$(dirname "$ROOT")" "$(basename "$ROOT")"

echo "===== 2/7 备份数据库 ====="
sudo -u postgres pg_dump -Fc snail_chat > "$BACKUP_ROOT/snail_chat_before_v030_${STAMP}.dump"

echo "===== 3/7 执行数据库迁移 ====="
sudo -u postgres psql snail_chat -v ON_ERROR_STOP=1 -f "$ROOT/backend/migrations/020_commercial_platform.sql"

echo "===== 4/7 后端语法检查 ====="
source "$ROOT/backend/venv/bin/activate"
python -m compileall -q "$ROOT/backend/app"
python -c "from app.main import app; print('FastAPI import OK / version:', app.version)" 2>/dev/null || \
  (cd "$ROOT/backend" && python -c "from app.main import app; print('FastAPI import OK / version:', app.version)")

echo "===== 5/7 重启后端 ====="
systemctl restart snail-api
sleep 3
systemctl --no-pager --full status snail-api | sed -n '1,25p'

echo "===== 6/7 构建前端 ====="
cd "$ROOT/frontend"
npm run build

echo "===== 7/7 重启前端 ====="
pm2 restart snail-admin
pm2 status

echo
echo "=========================================="
echo "蜗牛群聊精灵 v0.3.0 商业化基础版升级完成"
echo "代码备份：$BACKUP_ROOT/snail-chat-elf-before-v030_${STAMP}.tar.gz"
echo "数据库备份：$BACKUP_ROOT/snail_chat_before_v030_${STAMP}.dump"
echo "=========================================="
