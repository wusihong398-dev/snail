# CODEX_HANDOFF.md

# 蜗牛群聊精灵（Snail Chat Elf）项目接管说明

> 用途：本文件用于交接给 Codex / 新开发者 / 新会话继续开发。  
> 当前项目已进入 **v0.3.0 商业化基础版**。  
> 接管时应优先保持现有线上功能稳定，不要推倒重写，不要删除已存在的数据结构和兼容字段。

---

## 1. 项目架构

项目名称：**蜗牛群聊精灵**

核心定位：微信群 AI 机器人管理平台，已经从单一后台逐步升级为“平台超级管理员 → 代理商 → 购买程序客户 / Owner → 微信群 → 群管理员 → 普通群成员”的商业化体系。

当前主要技术栈：

```text
后端：FastAPI + Uvicorn + SQLAlchemy Async
数据库：PostgreSQL
缓存：Redis
前端：Next.js 16.3.1 + React + TypeScript + Ant Design
前端进程：PM2
后端进程：systemd
公网域名：https://jeyav.cn
后台：https://jeyav.cn/admin
API：https://jeyav.cn/api
```

项目根目录：

```text
/data/snail-chat-elf
```

主要结构：

```text
/data/snail-chat-elf/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── auth/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   └── services/
│   ├── migrations/
│   │   └── 020_commercial_platform.sql
│   └── venv/
├── frontend/
│   ├── app/
│   │   ├── admin/
│   │   │   ├── page.tsx
│   │   │   └── components/
│   │   │       ├── CommercialCenter.tsx
│   │   │       ├── LoveCenter.tsx
│   │   │       ├── BabyCenter.tsx
│   │   │       ├── ShopCenter.tsx
│   │   │       ├── SettingsCenter.tsx
│   │   │       ├── UserCenter.tsx
│   │   │       ├── WechatCenter.tsx
│   │   │       └── GroupCenter.tsx
│   │   └── lib/api.ts
│   └── node_modules/
├── UPGRADE_TO_V0.3.0.sh
├── DEPLOY_v0.3.0.md
└── CHANGELOG_v0.3.0.md
```

---

## 2. 当前版本

当前线上版本：

```text
v0.3.0
```

API 健康检查当前已验证返回：

```json
{
  "app":"蜗牛群聊精灵",
  "service":"snail-chat-elf-api",
  "version":"0.3.0",
  "database":"connected",
  "redis":"connected"
}
```

当前商业化迁移：

```text
backend/migrations/020_commercial_platform.sql
```

升级脚本：

```text
/data/snail-chat-elf/UPGRADE_TO_V0.3.0.sh
```

升级完成时脚本已生成备份，例如：

```text
/data/snail-chat-elf-backups/snail-chat-elf-before-v030_20260831_203355.tar.gz
/data/snail-chat-elf-backups/snail_chat_before_v030_20260831_203355.dump
```

后续恢复前必须先检查实际最新备份文件时间。

---

## 3. 已完成功能

### 3.1 管理后台模块

当前 `/admin` 顶部主要模块：

```text
数据中心
AI中心
微信机器人
用户中心
商业中心
恋爱系统
宝宝系统
代理授权
系统设置
```

### 3.2 用户系统

已存在核心字段：

```text
id
wx_user_id
nickname
avatar
level
coins
paid_diamonds
bonus_diamonds
experience
is_active
member_level
member_started_at
member_expire_at
created_at
```

资产规则：

```text
coins：蜗币，主要通过任务 / 活动 / 游戏获得
paid_diamonds：真实付费钻石
bonus_diamonds：会员赠送 / 活动 / 群管理员赠送钻石
```

钻石消费原则：优先消耗 `bonus_diamonds`，再消耗 `paid_diamonds`。

### 3.3 商城 / 订单 / 蜗币流水

已有商城、订单、蜗币消费、会员商品基础。

已测试商品：

```text
VIP 30天
玫瑰礼物
```

已验证流程：

```text
购买商品
→ 扣蜗币
→ 写订单
→ 写 coin_transactions
→ 会员有效期增加 / 礼物生效
```

### 3.4 礼物系统

已存在：

```text
gift_products
gift_records
```

已测试：用户1向用户2赠送玫瑰，发送方扣蜗币、写订单，接收方增加经验，双方增加亲密度。

系统设置已支持：

```text
gift_exp_multiplier
gift_intimacy_multiplier
```

### 3.5 恋爱 / 婚姻系统

关系状态：

```text
normal
love
married
```

已完成：

```text
亲密度
恋爱申请
接受 / 拒绝
求婚申请
接受 / 拒绝
结婚时间记录
```

系统设置：

```text
love_intimacy_threshold
marriage_intimacy_threshold
```

当前正式结婚门槛已恢复：

```text
500
```

多伴侣基础额度：

```text
普通用户：1
VIP：2
SVIP：3
```

系统设置：

```text
normal_max_partners
vip_max_partners
svip_max_partners
```

v0.3.0 已增加永久额外权益：

```text
extra_partner_slots
```

真实伴侣上限 = 会员基础额度 + 永久额外伴侣槽。

默认扩容设置：

```text
partner_slot_diamond_price = 500
max_extra_partner_slots = 3
```

重要规则：钻石只能购买“名额”，不能强制建立恋爱 / 婚姻关系；仍必须满足亲密度并由对方同意。

### 3.6 宝宝系统

已完成：

```text
Baby
BabyRequest
发起宝宝申请
接受 / 拒绝
必须 married 后才能创建宝宝
```

宝宝字段：

```text
id
name
parent_user_id_a
parent_user_id_b
gender
level
experience
happiness
hunger
health
born_at
created_at
```

当前已验证测试宝宝：

```text
名称：小蜗牛
父母：用户1 + 用户2
性别：female
等级：1
经验：0
快乐：100
饥饿：100
健康：100
```

会员宝宝额度：

```text
普通：每对1，个人总数1
VIP：每对2，个人总数4
SVIP：每对3，个人总数6
```

系统设置：

```text
normal_max_children_per_couple
vip_max_children_per_couple
svip_max_children_per_couple
normal_max_children_total
vip_max_children_total
svip_max_children_total
```

v0.3.0 已增加：

```text
extra_baby_slots
baby_slot_diamond_price = 200
max_extra_baby_slots = 6
```

### 3.7 会员体系

旧兼容字段仍在：

```text
users.member_level
users.member_started_at
users.member_expire_at
```

v0.3.0 新增正式商业结构：

```text
membership_plans
membership_plan_entitlements
membership_products
user_memberships
```

默认方案：

```text
normal
vip
svip
```

会员商品支持：

```text
duration_days
price_cents
diamond_price
bonus_diamonds
bonus_grant_mode
```

赠钻模式：

```text
immediate
monthly
```

### 3.8 钻石系统

两类钻石必须永久分账：

```text
paid_diamonds
bonus_diamonds
```

钻石流水表：

```text
diamond_transactions
```

记录：

```text
user_id
transaction_type
diamond_type
amount
paid_before
paid_after
bonus_before
bonus_after
reference_type
reference_id
description
created_at
```

已完成真实测试：代理商生成100钻石码，代理钻石额度 `10000 → 9900`，用户3 `paid_diamonds 0 → 100`，流水正确写入。

### 3.9 代理商体系

商业层级：

```text
平台超级管理员
→ 代理商
→ 购买程序客户 / Owner
→ 微信群
→ 群管理员
→ 普通群成员
```

代理模式：

```text
commission
prepaid
hybrid
```

代理商字段：

```text
name
agent_code
agent_type
commission_rate
enabled
parent_agent_id
license_balance
diamond_quota
created_at
```

当前测试代理商：

```text
测试代理商A
agent_code = TEST_AGENT_A
agent_type = prepaid
授权库存 = 9
钻石销售额度 = 9900
客户数 = 1
```

### 3.10 客户 / Owner 体系

表：

```text
customers
```

核心字段：

```text
agent_id
owner_user_id
name
plan_code
license_status
license_started_at
license_expire_at
max_groups
enabled
created_at
```

当前测试客户：

```text
客户ID：1
agent_id：1
owner_user_id：3
name：蜗牛测试群001
plan_code：basic
license_status：active
max_groups：3
```

购买程序的微信号就是 Owner。

### 3.11 多群 / 群归属 / 群成员

`groups` 已新增：

```text
customer_id
```

群归属：

```text
customer_group_ownerships
```

群成员：

```text
group_members
```

同一个微信号可以加入多个群，并在不同群拥有不同角色，例如：

```text
群A：admin
群B：member
群C：owner
```

用户资产和会员全局唯一，不因为多群重复创建。

全局微信风控设置：

```text
wechat_max_groups_per_account = 20
```

实际可管理群数量：

```text
min(客户套餐上限, 微信全局风控上限)
```

### 3.12 群管理员权限结构

表：

```text
group_admin_permissions
```

后续权限应按：

```text
customer_id
group_id
user_id
permission_key
```

隔离，不能使用全局 admin 角色代替。

### 3.13 授权码 / 兑换码系统

核心表：

```text
redeem_codes
redeem_code_usages
```

支持 code_type：

```text
group_license
diamonds
membership
partner_slot
baby_slot
```

当前真正已开放并实测：

```text
group_license
diamonds
```

当前预留但 `/codes/redeem` 尚未开放完整兑换：

```text
membership
partner_slot
baby_slot
```

授权码安全规则：

- 高熵随机。
- 默认一次性。
- 有有效期。
- 使用后变 `redeemed`。
- 重复兑换被拒绝。
- 数据库只保存 `code_prefix + code_hash`，不保存完整明文。
- 完整代码只在生成成功时展示一次。

已完成群管理授权码真实测试：

```text
代理商生成 group_license
→ license_balance 10 → 9
→ 购买者在目标群兑换
→ 自动创建/找到用户
→ 自动创建/找到群
→ 自动创建 Customer
→ 绑定当前群
→ 当前微信号成为 owner
→ 写 customer_group_ownerships
→ 写 group_members
→ 写 redeem_code_usages
→ 授权码变 redeemed
→ 第二次兑换被拒绝
```

已完成钻石码真实测试：

```text
代理商生成100钻石码
→ diamond_quota 10000 → 9900
→ 用户兑换
→ paid_diamonds +100
→ diamond_transactions 写入
→ redeem_code_usages 写入
```

### 3.14 代理授权后台

组件：

```text
frontend/app/admin/components/CommercialCenter.tsx
```

当前页面已正常显示：

```text
代理商：1
购买客户：1
有效授权码：0
成功兑换：2
用户付费钻石余额：100
用户奖励钻石余额：0
```

当前标签：

```text
代理商管理
客户管理
授权码中心
兑换记录
钻石流水
会员商品
```

当前可用：

```text
新增代理商
生成授权码
查看代理商
查看客户
查看授权码
查看兑换记录
查看钻石流水
查看会员方案 / 商品
```

---

## 4. 当前服务器 / 客户端结构

### 4.1 后端服务

systemd：

```text
snail-api.service
```

检查：

```bash
systemctl status snail-api --no-pager
```

重启：

```bash
systemctl restart snail-api
```

日志：

```bash
journalctl -u snail-api -n 200 --no-pager
```

### 4.2 前端

PM2 应用：

```text
snail-admin
```

检查：

```bash
pm2 status
```

重启：

```bash
pm2 restart snail-admin
```

日志：

```bash
pm2 logs snail-admin --lines 100 --nostream
```

前端本地：

```text
http://127.0.0.1:3000
```

线上：

```text
https://jeyav.cn/admin
```

API：

```text
https://jeyav.cn/api
```

### 4.3 前端鉴权

`frontend/app/lib/api.ts` 使用 Axios，自动从：

```text
localStorage.getItem("token")
```

读取 JWT，并写入：

```text
Authorization: Bearer <token>
```

商业化 API 需要管理员登录。

---

## 5. 已知问题 / 当前缺口

### 5.1 代理后台仍偏查看型

缺：

```text
编辑代理商
启用/停用代理商
增加授权库存
增加钻石销售额度
修改佣金比例
客户续期
修改最大群数
暂停/恢复客户授权
查看绑定微信群
冻结授权码
作废授权码
搜索/筛选
```

### 5.2 会员 / 扩容兑换码仍为预留

`membership / partner_slot / baby_slot` 代码类型已存在，但当前兑换接口对这些类型仍返回未开放。

### 5.3 微信机器人真实消息入口尚未完整接入

当前 API 已有：

```text
POST /api/commercial/codes/redeem
```

但真实生产流程：

```text
微信群消息
→ @机器人
→ 解析授权码
→ 识别发送人 / 当前群
→ 调用 redeem API
→ 群内回复结果
```

还未完成完整接入。

### 5.4 短时群管理网页尚未完成

表：

```text
group_admin_sessions
```

已存在，但：

```text
生成短时 session
签发 URL
token 验证
按群过滤
权限拦截
```

尚未完整上线。

### 5.5 数据中心部分数字仍是静态占位

数据首页的微信机器人、微信群、注册用户、智能调用等统计还没有全部接真实 API。

### 5.6 PM2 日志存在 Next.js Server Action 噪声

偶尔出现：

```text
The Server Reference ID did not match the expected format.
```

目前不影响 `npm run build`、`next start`、`/admin` 和商业 API，不是当前阻塞问题。

### 5.7 浏览器 Token 失效时商业页面可能显示全 0

处理：

```text
退出后台
重新登录
Ctrl + F5
```

开发者工具可检查：

```javascript
localStorage.getItem("token")
```

---

## 6. 不能改的地方 / 强约束

### 6.1 不得删除旧兼容字段

不要删除：

```text
users.coins
users.member_level
users.member_started_at
users.member_expire_at
```

旧逻辑仍依赖。

### 6.2 付费钻石和奖励钻石不能合并

必须保留：

```text
paid_diamonds
bonus_diamonds
```

### 6.3 群管理员不能制造付费钻石

群管理员只允许赠送：

```text
coins
bonus_diamonds
```

`paid_diamonds` 只能来自真实购买、代理商钻石码、未来正式支付渠道。

### 6.4 会员过期不能删除已有关系和宝宝

禁止：

```text
自动删除伴侣
自动离婚
删除宝宝
```

正确逻辑：保留已有内容，只限制继续新增超额内容。

### 6.5 钻石不能强制建立恋爱关系

钻石只购买名额 / 会员 / 道具；恋爱和结婚继续走亲密度 + 申请 + 对方同意。

### 6.6 群权限不能做成全局管理员

必须按：

```text
customer_id + group_id + user_id
```

隔离。

### 6.7 授权码数据库不能保存完整明文

继续保持：

```text
code_prefix
code_hash
```

完整码只生成时返回一次。

### 6.8 已经执行过的数据库迁移不要回头改

`020_commercial_platform.sql` 已在生产执行。

后续新增：

```text
021_xxx.sql
022_xxx.sql
```

不要继续修改 020 并重复执行。

### 6.9 生产修改必须先备份

每次大改：

```text
备份 → 修改 → 静态检查 → 构建 → 重启 → 验收
```

不要直接覆盖。

---

## 7. 下一阶段任务

### P0：代理后台运营化

后端建议新增：

```text
PUT  /commercial/agents/{id}
POST /commercial/agents/{id}/license-balance
POST /commercial/agents/{id}/diamond-quota
POST /commercial/agents/{id}/enable
POST /commercial/agents/{id}/disable

PUT  /commercial/customers/{id}
POST /commercial/customers/{id}/renew
POST /commercial/customers/{id}/pause
POST /commercial/customers/{id}/resume

POST /commercial/codes/{id}/freeze
POST /commercial/codes/{id}/void
```

所有库存 / 钻石额度变化必须写独立流水，不能只修改余额。

前端增加：

```text
代理商：编辑 / 加库存 / 加钻石额度 / 停用
客户：续期 / 改群数 / 暂停 / 恢复 / 查看绑定群
授权码：冻结 / 作废 / 筛选
兑换记录：搜索 / 筛选
钻石流水：搜索 / 筛选
会员商品：新增 / 编辑 / 上下架
```

### P1：接入真实微信群授权消息入口

支持：

```text
@机器人 + 群管理授权码
@机器人 + 钻石兑换码
```

必须增加机器人服务签名 / API Secret，不能只依赖高熵授权码。

### P2：群管理员系统

支持 Owner：

```text
授权管理员
撤销管理员
逐项权限
不同群不同权限
```

### P3：短时群后台

支持：

```text
@机器人 管理后台
```

生成 5~10 分钟有效的短时 URL，绑定当前 customer / group / user / permission。

### P4：新人欢迎语

支持模板变量：

```text
{nickname}
{group_name}
{member_count}
{date}
{admin_name}
```

### P5：重要聊天记录 / 群记忆

普通会员：文字；高级会员：文字+图片；更高级会员：文字+图片+视频；视频单文件不超过 200MB。

建议新增：

```text
group_messages
saved_group_messages
saved_message_attachments
```

媒体不要直接存 PostgreSQL 二进制，数据库只存 URL / 大小 / MIME / hash / 元数据。

### P6：抽奖系统

建议：

```text
lotteries
lottery_prizes
lottery_entries
lottery_winners
```

奖品可支持实物、会员、钻石、蜗币、道具。

### P7：宝宝成长玩法

后续：

```text
喂养
陪玩
洗澡
睡觉
看病
宝宝礼物
成长记录
升级
```

商业授权和群权限优先级高于宝宝成长。

---

## 8. 测试方法

### 8.1 后端语法 / 导入

```bash
cd /data/snail-chat-elf/backend
source venv/bin/activate
python -m compileall -q app
python -c "from app.main import app; print('FastAPI import OK'); print(app.version)"
```

预期：

```text
FastAPI import OK
0.3.0
```

### 8.2 服务状态

```bash
systemctl status snail-api --no-pager
pm2 status
```

### 8.3 健康检查

```bash
curl -s https://jeyav.cn/api/health
```

### 8.4 前端构建

```bash
cd /data/snail-chat-elf/frontend
npm run build
```

必须成功完成 TypeScript 和静态页面生成。

### 8.5 基础回归

```bash
curl -s https://jeyav.cn/api/users
curl -s https://jeyav.cn/api/relationships
curl -s https://jeyav.cn/api/babies
curl -s https://jeyav.cn/api/shop/products
```

### 8.6 商业 API

管理员登录获取 Token，注意不要把真实密码 / JWT 写入源码或本文件。

```bash
TOKEN="<ADMIN_TOKEN>"
```

测试：

```bash
curl -s https://jeyav.cn/api/commercial/agents -H "Authorization: Bearer $TOKEN"

curl -s https://jeyav.cn/api/commercial/customers -H "Authorization: Bearer $TOKEN"

curl -s https://jeyav.cn/api/commercial/code-usages -H "Authorization: Bearer $TOKEN"

curl -s https://jeyav.cn/api/commercial/diamond-transactions -H "Authorization: Bearer $TOKEN"
```

### 8.7 群管理授权码回归

生成 `group_license` 后模拟兑换：

```json
{
  "code":"<CODE>",
  "wx_user_id":"wx_owner_test001",
  "wx_group_id":"wx_group_test001",
  "nickname":"测试购买者",
  "group_name":"蜗牛测试群001"
}
```

验证：

```sql
SELECT * FROM customer_group_ownerships ORDER BY id DESC;
SELECT * FROM group_members ORDER BY id DESC;
SELECT * FROM redeem_code_usages ORDER BY id DESC;
```

并再次使用同一 code，必须失败。

### 8.8 钻石码回归

兑换后验证：

```text
paid_diamonds 增加
bonus_diamonds 不变
agent.diamond_quota 减少
diamond_transactions 新增
redeem_code_usages 新增
```

---

## 9. 部署方法

### 9.1 部署前备份

代码：

```bash
STAMP="$(date +%Y%m%d_%H%M%S)"
mkdir -p /data/snail-chat-elf-backups

tar --exclude='snail-chat-elf/frontend/node_modules' --exclude='snail-chat-elf/frontend/.next' --exclude='snail-chat-elf/backend/venv' -zcf "/data/snail-chat-elf-backups/snail-chat-elf_${STAMP}.tar.gz" -C /data snail-chat-elf
```

数据库：

```bash
sudo -u postgres pg_dump -Fc snail_chat > "/data/snail-chat-elf-backups/snail_chat_${STAMP}.dump"
```

### 9.2 后端更新

```bash
cd /data/snail-chat-elf/backend
source venv/bin/activate
python -m compileall -q app
python -c "from app.main import app; print(app.version)"
systemctl restart snail-api
sleep 3
systemctl status snail-api --no-pager
```

### 9.3 数据库迁移

新增功能必须创建新的 migration，例如：

```text
021_agent_operations.sql
022_group_admin_sessions.sql
```

执行前必须人工查看 SQL：

```bash
sudo -u postgres psql snail_chat -v ON_ERROR_STOP=1 -f backend/migrations/021_xxx.sql
```

### 9.4 前端更新

```bash
cd /data/snail-chat-elf/frontend
npm run build
pm2 restart snail-admin
```

### 9.5 公网验收

```bash
curl -I https://jeyav.cn/admin
curl -s https://jeyav.cn/api/health
```

浏览器强制刷新：

```text
Ctrl + F5
```

---

## 10. 回滚方法

列出备份：

```bash
ls -lht /data/snail-chat-elf-backups/
```

代码回滚时确认备份时间和数据库备份时间一致。

数据库高风险回滚：

```bash
sudo -u postgres pg_restore --clean --if-exists -d snail_chat /data/snail-chat-elf-backups/<BACKUP>.dump
```

只有确认代码版本 / 数据库版本 / 备份时间匹配后才能执行。

---

## 11. Codex 接管规则

1. 先读本文件。
2. 先读取当前真实文件，不根据旧聊天猜代码。
3. 修改前备份。
4. 不大规模重写正常模块。
5. 优先增量迁移。
6. 所有数据库迁移必须可回滚。
7. 后端每次改完执行 `python -m compileall -q app`。
8. 前端每次改完执行 `npm run build`。
9. 不在生产数据库做危险 `DROP / DELETE`。
10. 不清空用户、关系、宝宝、商城订单、授权码流水。
11. 不在源码写管理员密码、JWT、API Secret。
12. 商业接口必须检查 agent / customer / group / user / permission 作用域。
13. 下一阶段真实机器人兑换入口必须增加机器人服务签名。
14. 授权码继续哈希存储。
15. 付费钻石和奖励钻石永久分账。
16. 已上线的 `020_commercial_platform.sql` 不再修改，新增迁移从 021 开始。

---

## 12. 当前状态总结

```text
基础后台                   已完成
AI模块                     已存在
微信机器人后台             已存在
用户系统                   已完成基础
商城                       已完成基础
蜗币                       已完成
礼物                       已完成
亲密度                     已完成
恋爱申请                   已完成
结婚申请                   已完成
多伴侣基础额度             已完成
宝宝                       已完成
宝宝申请                   已完成
会员宝宝额度               已完成
付费钻石/奖励钻石           已完成
钻石流水                   已完成
永久伴侣槽                 已完成基础
永久宝宝槽                 已完成基础
代理商                     已完成基础
购买客户                   已完成基础
群归属                     已完成基础
群成员独立身份             已完成基础
群管理员权限表             已完成结构
群管理授权码               已完成并实测
钻石兑换码                 已完成并实测
授权码审计                 已完成并实测
代理授权后台               已完成基础展示
代理后台运营操作           待开发
真实微信群授权消息入口      待开发
短时群管理网页             待开发
欢迎语                     待开发
重要聊天保存               待开发
文字/图片/视频会员保存权益  待开发
抽奖                       待开发
宝宝成长玩法               待开发
```

---

**接管原则：保持当前 v0.3.0 正常线上能力，继续增量开发，不推倒重写。**
