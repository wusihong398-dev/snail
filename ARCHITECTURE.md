# ARCHITECTURE.md

# 系统架构

生产根目录：`/data/snail-chat-elf`

```text
Internet
  -> Nginx / jeyav.cn
       -> /api/*  FastAPI/Uvicorn :8000
       -> /admin  Next.js :3000
```

后端：FastAPI、SQLAlchemy Async、PostgreSQL、Redis、Uvicorn，systemd 服务 `snail-api.service`。

前端：Next.js 16.3.1、React、TypeScript、Ant Design、Axios，PM2 应用 `snail-admin`。

## 商业层级
```text
平台超级管理员
 -> 代理商 Agent
 -> 购买客户 Customer
 -> Owner 微信号
 -> 微信群 Group
 -> 群管理员 / 群成员
```

同一个微信用户全局唯一，可进入多个群；群身份和管理权限独立。

## 资产
- `coins`：任务/签到/游戏等活跃货币。
- `paid_diamonds`：真实购买、代理商钻石码。
- `bonus_diamonds`：会员赠送、活动、管理员赠送。
- 钻石消费优先奖励钻石，再付费钻石。

## 商业核心表
`agents`, `customers`, `customer_group_ownerships`, `group_members`,
`group_admin_permissions`, `redeem_codes`, `redeem_code_usages`,
`diamond_transactions`, `admin_asset_grants`, `agent_commissions`,
`agent_license_transactions`, `group_admin_sessions`,
`membership_plans`, `membership_plan_entitlements`,
`membership_products`, `user_memberships`, `user_entitlements`。

## 关系
`normal -> love -> married -> baby`。
恋爱/婚姻必须满足亲密度、申请、对方同意。
容量 = 会员基础额度 + 永久扩容。
会员过期不删除已有关系和宝宝。

## 授权码
已开放：`group_license`, `diamonds`。
预留：`membership`, `partner_slot`, `baby_slot`。

## 计划中的微信群入口
- `@机器人 + 群授权码`
- `@机器人 + 钻石码`
- `@机器人 设置管理员 @某人`
- `@机器人 管理后台`
- `@机器人 保存`
- `@机器人 保存最近N条`
