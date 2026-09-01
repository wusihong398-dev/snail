# NEXT_TASK.md

# 当前任务：代理授权后台运营化

## 目标
在不破坏 v0.3.0 已上线功能和数据的前提下，把代理授权中心升级为可日常运营版本。

## 后端
新增或完善：
- 编辑代理商
- 启用/停用代理商
- 增加/调整授权库存，并写独立流水
- 增加/调整钻石销售额度，并写独立流水
- 修改佣金比例
- 客户续期
- 客户暂停/恢复
- 修改客户最大群数
- 查询客户绑定群
- 授权码冻结
- 授权码作废
- 兑换记录筛选
- 钻石流水筛选

如果需要数据库变更，新建 `021_commercial_operations.sql`，禁止修改已上线的 020。

## 前端
完善 `frontend/app/admin/components/CommercialCenter.tsx`：
- 代理商：编辑、加库存、加额度、停用/启用
- 客户：详情、续期、改最大群数、暂停/恢复、查看绑定群
- 授权码：筛选、冻结、作废
- 兑换记录：代理商/微信号/群/日期筛选
- 钻石流水：用户/类型/日期筛选
- 会员商品：新增、编辑、上下架

## 安全
- 所有操作校验代理/客户/群作用域。
- 资产与库存变化必须流水化。
- 不允许修改 paid_diamonds 为奖励用途。
- 不允许删除历史兑换和财务流水。

## 完成标准
```bash
cd /data/snail-chat-elf/backend
source venv/bin/activate
python -m compileall -q app

cd /data/snail-chat-elf/frontend
npm run build

systemctl restart snail-api
pm2 restart snail-admin
curl -s https://jeyav.cn/api/health
```

然后回归用户、商城、恋爱、婚姻、宝宝、代理商、客户、授权码和钻石流水。
