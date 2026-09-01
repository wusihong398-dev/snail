# SECURITY.md

# 安全规则

## 授权码
- 高熵随机。
- 数据库只保存 hash + 前缀。
- 完整码只显示一次。
- 默认一次性、有有效期。
- 使用事务和行锁避免重复兑换。
- 正式机器人调用增加 API Secret/HMAC。
- 后续记录失败兑换审计。

## 资产
- `paid_diamonds` / `bonus_diamonds` 分账。
- 群管理员只能赠 `coins` 和 `bonus_diamonds`。
- 关键资产操作记录 operator、target、customer、group、before、after、amount、reason、timestamp、reference。

## 代理
- 只能管理自己名下客户。
- prepaid/hybrid 生成授权/钻石码必须扣库存/额度。
- 库存/额度调整必须有流水。
- 退款佣金必须可冲销。
- `parent_agent_id` 只预留，不擅自开放无限多级代理。

## 群权限
所有管理权限绑定 `customer_id + group_id + user_id`。
一个群的管理员权限不能自动继承到其他群。

## 会员/关系
会员过期不删除关系和宝宝；钻石不能强制恋爱/结婚；扩容只改变容量。

## 凭证
管理员密码、JWT、数据库密码、机器人 Secret、API Key、支付密钥禁止提交到仓库。

## 媒体
未来群记忆视频单文件 <= 200MB。媒体文件存对象存储/媒体目录，PostgreSQL 保存 URL、hash、大小、MIME、消息元数据。
