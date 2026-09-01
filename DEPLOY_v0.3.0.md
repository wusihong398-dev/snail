# v0.3.0 部署说明

## 推荐升级方法

将新版完整目录覆盖/同步到服务器 `/data/snail-chat-elf` 后：

```bash
cd /data/snail-chat-elf
chmod +x UPGRADE_TO_V0.3.0.sh
./UPGRADE_TO_V0.3.0.sh /data/snail-chat-elf
```

脚本会先备份代码和 PostgreSQL，再执行迁移、检查、构建和重启。

## 升级后检查

```bash
curl https://jeyav.cn/api/health
```

应看到版本 `0.3.0`、数据库和 Redis 均 connected。

登录 `/admin` 后应新增“代理授权”。

## 群管理授权码流程

1. 平台后台 → 代理授权 → 新增代理商。
2. 生成 `群管理授权码`，`value` 可填写授权天数；0 表示默认 365 天。
3. 代理商把完整代码发给购买者。
4. 微信机器人收到购买者在目标群发送的 `@机器人 + 代码` 后，调用：

```http
POST /api/commercial/codes/redeem
```

请求示例：

```json
{
  "code": "WNA-GRP-XXXX-XXXX-XXXX-XXXX",
  "wx_user_id": "wxid_xxx",
  "wx_group_id": "group_xxx",
  "nickname": "购买者昵称",
  "group_name": "微信群名称"
}
```

成功后购买者微信号成为该客户/群的 Owner，后台写入精确激活时间。

## 钻石兑换码流程

代理授权中心生成 `钻石兑换码`，value 填钻石数量。微信机器人使用同一个兑换接口，群字段可为空。兑换成功增加 `paid_diamonds` 并写 `diamond_transactions`。

## 安全说明

- 代理授权后台 API 要求管理员 Bearer Token。
- 群内兑换接口公开给机器人调用，但必须持有高熵一次性授权码。
- 数据库只保存授权码哈希，完整代码仅生成时展示一次。
- 正式机器人接入时建议再增加“机器人服务签名/API Secret”，限制兑换接口只能由你的机器人服务调用。
