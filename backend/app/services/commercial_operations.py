"""Atomic helpers: caller commits/rolls back. Lock order is
agent -> code -> user -> customer -> group. Missing identities are serialized
by advisory transaction locks at their resource level, before their row locks.
"""
from sqlalchemy import select, text
from fastapi import HTTPException
from app.models.commercial import Agent
from app.models.commercial_operations import AgentDiamondQuotaTransaction, AgentLicenseTransaction
from app.models.user import User
from app.services.diamonds import add_paid_diamonds, add_bonus_diamonds

MAX_BALANCE = 2147483647
TYPES = {"initial", "code_reserve", "code_release", "admin_adjustment", "manual_grant", "correction"}


async def lock_agent(db, agent_id):
    agent = (await db.execute(select(Agent).where(Agent.id == agent_id).with_for_update()
                             .execution_options(populate_existing=True))).scalar_one_or_none()
    if agent is None:
        raise HTTPException(404, "代理商不存在")
    return agent


async def lock_user(db, user_id):
    user = (await db.execute(select(User).where(User.id == user_id).with_for_update()
                            .execution_options(populate_existing=True))).scalar_one_or_none()
    if user is None:
        raise HTTPException(404, "用户不存在")
    return user


async def lock_identity(db, namespace, identity):
    await db.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:identity, 0))"),
                     {"identity": f"commercial:{namespace}:{identity}"})


def balance_after(before, amount):
    after = int(before or 0) + int(amount)
    if not 0 <= after <= MAX_BALANCE:
        raise HTTPException(400, "余额不足或超过允许上限")
    return after


async def _adjust(db, agent_id, amount, *, quota, transaction_type, operator_name,
                  reason, operator_type="admin", redeem_code_id=None,
                  customer_id=None, idempotency_key=None):
    if transaction_type not in TYPES or not operator_name or not reason:
        raise HTTPException(400, "调整类型、操作人及原因不能为空")
    agent = await lock_agent(db, agent_id)
    model = AgentDiamondQuotaTransaction if quota else AgentLicenseTransaction
    if idempotency_key:
        old = (await db.execute(select(model).where(model.agent_id == agent_id,
                   model.idempotency_key == idempotency_key))).scalar_one_or_none()
        if old:
            old_ref = old.redeem_code_id if quota else old.reference_id
            if (old.amount, old.transaction_type, old.operator_type, old.operator_name, old_ref,
                old.reason if quota else old.description) != (
                    amount, transaction_type, operator_type, operator_name, redeem_code_id, reason):
                raise HTTPException(409, "幂等键已用于不同资产调整")
            if quota and old.customer_id != customer_id:
                raise HTTPException(409, "幂等键客户不匹配")
            return old
    field = "diamond_quota" if quota else "license_balance"
    before = int(getattr(agent, field) or 0)
    after = balance_after(before, amount)
    common = dict(agent_id=agent_id, transaction_type=transaction_type, amount=amount,
                  operator_type=operator_type, operator_name=operator_name, idempotency_key=idempotency_key)
    if quota:
        tx = model(**common, quota_before=before, quota_after=after, reason=reason,
                   redeem_code_id=redeem_code_id, customer_id=customer_id)
    else:
        tx = model(**common, balance_before=before, balance_after=after, description=reason,
                   reference_type="redeem_code" if redeem_code_id else None, reference_id=redeem_code_id)
    setattr(agent, field, after)
    db.add(tx)
    await db.flush()
    return tx


async def adjust_agent_license_balance(db, agent_id, amount, **audit):
    return await _adjust(db, agent_id, amount, quota=False, **audit)


async def adjust_agent_diamond_quota(db, agent_id, amount, **audit):
    return await _adjust(db, agent_id, amount, quota=True, **audit)


def required_diamond_quota(value, max_uses):
    if value <= 0 or max_uses < 1:
        raise HTTPException(400, "钻石数量和使用次数必须大于0")
    total = int(value) * int(max_uses)
    if total > MAX_BALANCE:
        raise HTTPException(400, "预留额度超过允许上限")
    return total


async def reserve_diamond_quota_for_code(db, code, operator_name):
    required = required_diamond_quota(code.value, code.max_uses)
    if code.agent_id is None:
        raise HTTPException(400, "代理额度预留需要代理商")
    tx = await adjust_agent_diamond_quota(db, code.agent_id, -required,
        transaction_type="code_reserve", operator_name=operator_name, reason="生成钻石码预留全部使用次数额度",
        redeem_code_id=code.id, customer_id=code.customer_id, idempotency_key=f"code:{code.id}:reserve")
    code.reserved_total = required
    code.reservation_source = "agent_quota"
    return tx


async def release_unused_diamond_quota(db, code, operator_name, reason, idempotency_key):
    if code.code_type != "diamonds" or code.agent_id is None:
        raise HTTPException(400, "仅代理商钻石码支持额度返还")
    if code.status not in {"frozen", "void"}:
        raise HTTPException(409, "必须先冻结或作废授权码，再显式返还额度")
    if code.reservation_source != "agent_quota" or code.reserved_total is None:
        raise HTTPException(409, "历史或未确认预留的授权码禁止自动返还")
    ledger_key = f"code:{code.id}:release:{idempotency_key}"
    existing = (await db.execute(select(AgentDiamondQuotaTransaction).where(
        AgentDiamondQuotaTransaction.redeem_code_id == code.id,
        AgentDiamondQuotaTransaction.transaction_type == "code_release"))).scalar_one_or_none()
    remaining = max(0, int(code.reserved_total) - int(code.value) * int(code.used_count))
    if existing:
        if existing.idempotency_key != ledger_key:
            raise HTTPException(409, "该授权码的未用额度已经返还")
        return existing
    if remaining <= 0:
        raise HTTPException(409, "该授权码没有可返还的未用额度")
    return await adjust_agent_diamond_quota(db, code.agent_id, remaining,
        transaction_type="code_release", operator_name=operator_name, reason=reason,
        redeem_code_id=code.id, customer_id=code.customer_id,
        idempotency_key=ledger_key)


def reservation_summary(code):
    used = int(code.value) * int(code.used_count)
    return {"reservation_source": code.reservation_source or "legacy_unknown",
            "reserved_total": code.reserved_total, "used_total": used,
            "remaining_reserved": (None if code.reserved_total is None else max(0, code.reserved_total - used))}


async def grant_paid_diamonds(db, user, amount, **audit):
    return await add_paid_diamonds(db, user, amount, **audit)


async def grant_bonus_diamonds(db, user, amount, **audit):
    return await add_bonus_diamonds(db, user, amount, **audit)
