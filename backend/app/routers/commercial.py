from datetime import datetime, timedelta, timezone
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.group import Group
from app.models.commercial import (
    Agent, Customer, CustomerGroupOwnership, GroupMember,
    RedeemCode, RedeemCodeUsage, AdminAssetGrant,
    MembershipPlan, MembershipProduct, UserMembership,
)
from app.models.diamond import DiamondTransaction
from app.models.order import CoinTransaction
from app.models.commercial_operations import CommercialOperationLog, AgentLicenseTransaction, AgentDiamondQuotaTransaction
from app.schemas.commercial import (
    AgentCreate, AgentResponse, AgentUpdate, BalanceAdjustment, OperationRequest,
    CustomerResponse, CustomerUpdate, CustomerRenewRequest,
    RedeemCodeCreate, RedeemCodeGenerated, RedeemCodeListItem,
    RedeemRequest, RedeemResult, AssetGrantRequest, DiamondBalanceResponse,
    MembershipPlanCreate, MembershipPlanResponse, MembershipProductCreate,
    MembershipProductResponse, MembershipDiamondPurchase, EntitlementPurchaseRequest,
    CodeStatusRequest, CodeRefundRequest, MembershipProductUpdate,
)
from app.services.redeem_codes import generate_code, hash_code
from app.services.diamonds import spend_diamonds, total_diamonds
from app.services.commercial_operations import (
    lock_agent, lock_user, lock_identity, adjust_agent_license_balance,
    adjust_agent_diamond_quota, reserve_diamond_quota_for_code, required_diamond_quota,
    grant_paid_diamonds, grant_bonus_diamonds, reservation_summary, balance_after,
    release_unused_diamond_quota,
)
from app.auth.dependencies import require_admin
from app.services.entitlements import get_entitlement_quantity, add_entitlement
from app.services.system_settings import get_setting_int

router = APIRouter(prefix="/commercial", tags=["商业授权与代理"], dependencies=[Depends(require_admin)])
public_router = APIRouter(prefix="/commercial", tags=["授权码兑换"])

SUPPORTED_CODE_TYPES = {"group_license", "diamonds", "membership", "partner_slot", "baby_slot"}


def _page(page: int, page_size: int):
    if page < 1 or page_size < 1 or page_size > 200:
        raise HTTPException(400, "分页参数无效（page>=1，page_size为1到200）")
    return (page - 1) * page_size


async def _operation_once(db, operation_type, target_type, target_id, request_id):
    await lock_identity(db, "admin-operation", f"{operation_type}:{target_type}:{target_id}:{request_id}")
    return (await db.execute(select(CommercialOperationLog).where(
        CommercialOperationLog.operation_type == operation_type,
        CommercialOperationLog.target_type == target_type,
        CommercialOperationLog.target_id == target_id,
        CommercialOperationLog.request_id == request_id,
    ))).scalar_one_or_none()


def _log(operation_type, operator_name, target_type, target_id, before, after, reason, request_id):
    return CommercialOperationLog(operation_type=operation_type, operator_name=operator_name,
        target_type=target_type, target_id=target_id, request_id=request_id,
        details_json=json.dumps({"actor": operator_name, "action": operation_type,
            "before": before, "after": after, "reason": reason,
            "request_id": request_id}, ensure_ascii=False, default=str))


@router.get("/agents", response_model=list[AgentResponse])
async def list_agents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).order_by(Agent.id.desc()))
    return result.scalars().all()


@router.post("/agents", response_model=AgentResponse)
async def create_agent(data: AgentCreate, db: AsyncSession = Depends(get_db), operator_name: str = Depends(require_admin)):
    exists = await db.execute(select(Agent).where(Agent.agent_code == data.agent_code.strip()))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="代理商编码已存在")
    agent = Agent(
        name=data.name.strip(), agent_code=data.agent_code.strip(), agent_type=data.agent_type,
        commission_rate=data.commission_rate, license_balance=0, diamond_quota=0,
    )
    db.add(agent)
    await db.flush()
    await adjust_agent_license_balance(db, agent.id, data.license_balance, transaction_type="initial",
        operator_name=operator_name, reason="新建代理初始授权库存", idempotency_key="initial")
    await adjust_agent_diamond_quota(db, agent.id, data.diamond_quota, transaction_type="initial",
        operator_name=operator_name, reason="新建代理初始钻石额度", idempotency_key="initial")
    await db.commit(); await db.refresh(agent)
    return agent


@router.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: int, data: AgentUpdate, db: AsyncSession = Depends(get_db),
                       operator_name: str = Depends(require_admin)):
    old = await _operation_once(db, "agent_update", "agent", agent_id, data.request_id)
    if old:
        agent = await db.get(Agent, agent_id)
        if agent is None: raise HTTPException(404, "代理商不存在")
        return agent
    agent = await lock_agent(db, agent_id)
    before = {"name": agent.name, "agent_type": agent.agent_type, "commission_rate": float(agent.commission_rate)}
    agent.name, agent.agent_type, agent.commission_rate = data.name.strip(), data.agent_type, data.commission_rate
    after = {"name": agent.name, "agent_type": agent.agent_type, "commission_rate": float(agent.commission_rate)}
    db.add(_log("agent_update", operator_name, "agent", agent.id, before, after, data.reason, data.request_id))
    await db.commit(); await db.refresh(agent)
    return agent


async def _set_agent_enabled(agent_id, enabled, data, db, operator_name):
    op = "agent_enable" if enabled else "agent_disable"
    old = await _operation_once(db, op, "agent", agent_id, data.request_id)
    if old:
        return {"success": True, "agent_id": agent_id, "enabled": enabled, "idempotent": True}
    agent = await lock_agent(db, agent_id); before = agent.enabled; agent.enabled = enabled
    db.add(_log(op, operator_name, "agent", agent.id, before, enabled, data.reason, data.request_id))
    await db.commit()
    return {"success": True, "agent_id": agent.id, "enabled": enabled}


@router.post("/agents/{agent_id}/enable")
async def enable_agent(agent_id: int, data: OperationRequest, db: AsyncSession = Depends(get_db), operator_name: str = Depends(require_admin)):
    return await _set_agent_enabled(agent_id, True, data, db, operator_name)


@router.post("/agents/{agent_id}/disable")
async def disable_agent(agent_id: int, data: OperationRequest, db: AsyncSession = Depends(get_db), operator_name: str = Depends(require_admin)):
    return await _set_agent_enabled(agent_id, False, data, db, operator_name)


async def _adjust_agent(agent_id, data, db, operator_name, quota):
    fn = adjust_agent_diamond_quota if quota else adjust_agent_license_balance
    tx = await fn(db, agent_id, data.change, transaction_type="admin_adjustment",
        operator_name=operator_name, reason=data.reason, idempotency_key=data.request_id)
    await db.commit()
    before = int(tx.quota_before if quota else tx.balance_before)
    after = int(tx.quota_after if quota else tx.balance_after)
    return {"success": True, "agent_id": agent_id, "before": before, "change": int(tx.amount), "after": after,
            "actor": tx.operator_name, "reason": data.reason, "request_id": data.request_id}


@router.post("/agents/{agent_id}/license-balance")
async def adjust_license(agent_id: int, data: BalanceAdjustment, db: AsyncSession = Depends(get_db), operator_name: str = Depends(require_admin)):
    return await _adjust_agent(agent_id, data, db, operator_name, False)


@router.post("/agents/{agent_id}/diamond-quota")
async def adjust_quota(agent_id: int, data: BalanceAdjustment, db: AsyncSession = Depends(get_db), operator_name: str = Depends(require_admin)):
    return await _adjust_agent(agent_id, data, db, operator_name, True)


@router.get("/customers", response_model=list[CustomerResponse])
async def list_customers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).order_by(Customer.id.desc()))
    return result.scalars().all()


async def _customer_detail(db, customer_id):
    row = (await db.execute(select(Customer, User.wx_user_id).join(User, User.id == Customer.owner_user_id)
        .where(Customer.id == customer_id))).first()
    if row is None:
        raise HTTPException(404, "客户不存在")
    customer, owner_wx = row
    count = (await db.execute(select(func.count()).select_from(CustomerGroupOwnership)
        .where(CustomerGroupOwnership.customer_id == customer_id))).scalar_one()
    return {"id": customer.id, "agent_id": customer.agent_id, "owner_user_id": customer.owner_user_id,
        "owner_wx_user_id": owner_wx, "name": customer.name, "plan_code": customer.plan_code,
        "license_status": customer.license_status, "license_started_at": customer.license_started_at,
        "license_expire_at": customer.license_expire_at, "max_groups": customer.max_groups,
        "current_groups": count, "enabled": customer.enabled, "created_at": customer.created_at}


@router.get("/customers/{customer_id}")
async def get_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
    return await _customer_detail(db, customer_id)


@router.get("/customers/{customer_id}/groups")
async def customer_groups(customer_id: int, db: AsyncSession = Depends(get_db)):
    await _customer_detail(db, customer_id)
    rows = (await db.execute(select(CustomerGroupOwnership, Group).join(Group, Group.id == CustomerGroupOwnership.group_id)
        .where(CustomerGroupOwnership.customer_id == customer_id).order_by(CustomerGroupOwnership.id.desc()))).all()
    return [{"ownership_id": own.id, "group_id": group.id, "wx_group_id": group.wx_group_id,
        "group_name": group.group_name, "owner_user_id": own.owner_user_id, "activated_at": own.activated_at}
        for own, group in rows]


@router.put("/customers/{customer_id}")
async def update_customer(customer_id: int, data: CustomerUpdate, db: AsyncSession = Depends(get_db), operator_name: str = Depends(require_admin)):
    old = await _operation_once(db, "customer_update", "customer", customer_id, data.request_id)
    if old: return await _customer_detail(db, customer_id)
    customer = (await db.execute(select(Customer).where(Customer.id == customer_id).with_for_update())).scalar_one_or_none()
    if customer is None: raise HTTPException(404, "客户不存在")
    if data.agent_id is not None and await db.get(Agent, data.agent_id) is None: raise HTTPException(404, "代理商不存在")
    count = (await db.execute(select(func.count()).select_from(CustomerGroupOwnership)
        .where(CustomerGroupOwnership.customer_id == customer_id))).scalar_one()
    if data.max_groups < count: raise HTTPException(400, f"最大群数量不能低于当前绑定群数量{count}")
    before = {"name": customer.name, "agent_id": customer.agent_id, "plan_code": customer.plan_code, "max_groups": customer.max_groups}
    customer.name, customer.agent_id, customer.plan_code, customer.max_groups = data.name, data.agent_id, data.plan_code, data.max_groups
    after = {"name": customer.name, "agent_id": customer.agent_id, "plan_code": customer.plan_code, "max_groups": customer.max_groups}
    db.add(_log("customer_update", operator_name, "customer", customer.id, before, after, data.reason, data.request_id))
    await db.commit(); return await _customer_detail(db, customer_id)


@router.post("/customers/{customer_id}/renew")
async def renew_customer(customer_id: int, data: CustomerRenewRequest, db: AsyncSession = Depends(get_db), operator_name: str = Depends(require_admin)):
    old = await _operation_once(db, "customer_renew", "customer", customer_id, data.request_id)
    if old: return await _customer_detail(db, customer_id)
    customer = (await db.execute(select(Customer).where(Customer.id == customer_id).with_for_update())).scalar_one_or_none()
    if customer is None: raise HTTPException(404, "客户不存在")
    now = datetime.now(timezone.utc); before = customer.license_expire_at
    base = before if before and before > now else now
    customer.license_expire_at = base + timedelta(days=data.duration_days)
    if customer.license_started_at is None: customer.license_started_at = now
    customer.license_status = "active"; customer.enabled = True
    db.add(_log("customer_renew", operator_name, "customer", customer.id, before, customer.license_expire_at, data.reason, data.request_id))
    await db.commit(); return await _customer_detail(db, customer_id)


async def _set_customer_active(customer_id, enabled, data, db, operator_name):
    op = "customer_resume" if enabled else "customer_pause"
    old = await _operation_once(db, op, "customer", customer_id, data.request_id)
    if old: return await _customer_detail(db, customer_id)
    customer = (await db.execute(select(Customer).where(Customer.id == customer_id).with_for_update())).scalar_one_or_none()
    if customer is None: raise HTTPException(404, "客户不存在")
    before = {"enabled": customer.enabled, "license_status": customer.license_status}
    customer.enabled, customer.license_status = enabled, "active" if enabled else "paused"
    after = {"enabled": customer.enabled, "license_status": customer.license_status}
    db.add(_log(op, operator_name, "customer", customer.id, before, after, data.reason, data.request_id))
    await db.commit(); return await _customer_detail(db, customer_id)


@router.post("/customers/{customer_id}/pause")
async def pause_customer(customer_id: int, data: OperationRequest, db: AsyncSession = Depends(get_db), operator_name: str = Depends(require_admin)):
    return await _set_customer_active(customer_id, False, data, db, operator_name)


@router.post("/customers/{customer_id}/resume")
async def resume_customer(customer_id: int, data: OperationRequest, db: AsyncSession = Depends(get_db), operator_name: str = Depends(require_admin)):
    return await _set_customer_active(customer_id, True, data, db, operator_name)


@router.get("/codes")
async def list_codes(page: int = 1, page_size: int = 20, agent_id: int | None = None,
                     customer_id: int | None = None, code_type: str | None = None,
                     status: str | None = None, prefix: str | None = None,
                     created_from: datetime | None = None, created_to: datetime | None = None,
                     expires_from: datetime | None = None, expires_to: datetime | None = None,
                     db: AsyncSession = Depends(get_db)):
    offset = _page(page, page_size); filters = []
    for column, value in ((RedeemCode.agent_id, agent_id), (RedeemCode.customer_id, customer_id),
                          (RedeemCode.code_type, code_type), (RedeemCode.status, status)):
        if value is not None: filters.append(column == value)
    if prefix: filters.append(RedeemCode.code_prefix.ilike(f"%{prefix.strip()}%"))
    if created_from: filters.append(RedeemCode.created_at >= created_from)
    if created_to: filters.append(RedeemCode.created_at <= created_to)
    if expires_from: filters.append(RedeemCode.expires_at >= expires_from)
    if expires_to: filters.append(RedeemCode.expires_at <= expires_to)
    total = (await db.execute(select(func.count()).select_from(RedeemCode).where(*filters))).scalar_one()
    rows = (await db.execute(select(RedeemCode).where(*filters).order_by(RedeemCode.id.desc())
        .offset(offset).limit(page_size))).scalars().all()
    items = []
    for x in rows:
        summary = reservation_summary(x)
        items.append({**RedeemCodeListItem.model_validate(x).model_dump(), **summary,
            "refundable": summary["remaining_reserved"] if x.reservation_source == "agent_quota" else None})
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/codes", response_model=RedeemCodeGenerated)
async def create_code(data: RedeemCodeCreate, db: AsyncSession = Depends(get_db), operator_name: str = Depends(require_admin)):
    if data.code_type not in SUPPORTED_CODE_TYPES:
        raise HTTPException(status_code=400, detail="不支持的授权码类型")
    if data.request_id:
        # Request guard precedes resource locks; never entered from a later lock level.
        await lock_identity(db, "create-request", f"{operator_name}:{data.request_id}")
        previous = (await db.execute(select(RedeemCode.id).where(
            RedeemCode.created_by == operator_name, RedeemCode.request_id == data.request_id))).scalar_one_or_none()
        if previous is not None:
            raise HTTPException(409, "该请求已生成授权码；完整明文不会再次展示")
    agent = None
    if data.agent_id is not None:
        agent = await lock_agent(db, data.agent_id)
        if agent is None or not agent.enabled:
            raise HTTPException(status_code=404, detail="代理商不存在或已停用")
    if data.code_type == "diamonds" and data.value <= 0:
        raise HTTPException(status_code=400, detail="钻石兑换码数量必须大于0")
    if data.code_type == "diamonds":
        required_diamond_quota(data.value, data.max_uses)
    if data.customer_id is not None:
        customer = await db.get(Customer, data.customer_id)
        if customer is None or customer.agent_id != data.agent_id:
            raise HTTPException(400, "客户不存在或不属于所选代理商")
    code, prefix, digest = generate_code(data.code_type)
    now = datetime.now(timezone.utc)
    item = RedeemCode(
        code_prefix=prefix, code_hash=digest, code_type=data.code_type,
        agent_id=data.agent_id, customer_id=data.customer_id, value=data.value,
        valid_from=now, expires_at=now + timedelta(hours=data.expires_hours),
        max_uses=data.max_uses, used_count=0, status="active", created_by=operator_name,
        request_id=data.request_id,
    )
    db.add(item); await db.flush()
    if agent is not None and data.code_type == "diamonds":
        # All agent modes reserve the complete amount, not just prepaid/hybrid.
        await reserve_diamond_quota_for_code(db, item, operator_name)
    elif agent is not None and data.code_type == "group_license" and agent.agent_type in {"prepaid", "hybrid"}:
        await adjust_agent_license_balance(db, agent.id, -1, transaction_type="code_reserve",
            operator_name=operator_name, reason="生成客户群授权码", redeem_code_id=item.id,
            idempotency_key=f"code:{item.id}:reserve")
    if data.code_type == "diamonds" and agent is None:
        # Preserve existing platform issuance, but do not claim a quota reservation.
        item.reservation_source = "platform_manual"
    db.add(CommercialOperationLog(operation_type="code_create", operator_name=operator_name,
        target_type="redeem_code", target_id=item.id,
        details_json=json.dumps({"code_type": item.code_type, "value": item.value,
            "max_uses": item.max_uses, "agent_id": item.agent_id,
            "reservation_source": item.reservation_source, "reserved_total": item.reserved_total})))
    await db.commit(); await db.refresh(item)
    return RedeemCodeGenerated(
        id=item.id, code=code, code_type=item.code_type, agent_id=item.agent_id,
        customer_id=item.customer_id, value=item.value, expires_at=item.expires_at,
        max_uses=item.max_uses,
    )


async def _get_or_create_user(db: AsyncSession, wx_user_id: str, nickname: str | None):
    await lock_identity(db, "user", wx_user_id)
    result = await db.execute(select(User).where(User.wx_user_id == wx_user_id).with_for_update()
                              .execution_options(populate_existing=True))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(wx_user_id=wx_user_id, nickname=nickname or "", coins=0, experience=0)
        db.add(user); await db.flush()
    elif nickname and not user.nickname:
        user.nickname = nickname
    return user


async def _get_or_create_group(db: AsyncSession, wx_group_id: str, group_name: str | None):
    await lock_identity(db, "group", wx_group_id)
    result = await db.execute(select(Group).where(Group.wx_group_id == wx_group_id).with_for_update()
                              .execution_options(populate_existing=True))
    group = result.scalar_one_or_none()
    if group is None:
        group = Group(wx_group_id=wx_group_id, group_name=group_name or wx_group_id)
        db.add(group); await db.flush()
    elif group_name and not group.group_name:
        group.group_name = group_name
    return group


@public_router.post("/codes/redeem", response_model=RedeemResult)
async def redeem_code(data: RedeemRequest, db: AsyncSession = Depends(get_db)):
    digest = hash_code(data.code)
    # Read immutable ownership first, then acquire locks in the universal order.
    snapshot = (await db.execute(select(RedeemCode.id, RedeemCode.agent_id)
                                .where(RedeemCode.code_hash == digest))).first()
    if snapshot is None:
        raise HTTPException(404, "授权码不存在")
    if snapshot.agent_id is not None:
        await lock_agent(db, snapshot.agent_id)
    result = await db.execute(select(RedeemCode).where(RedeemCode.code_hash == digest).with_for_update()
                              .execution_options(populate_existing=True))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="授权码不存在")
    if item.agent_id != snapshot.agent_id:
        raise HTTPException(409, "授权码归属发生变化，请重试")
    if data.request_id:
        previous = (await db.execute(select(RedeemCodeUsage).where(
            RedeemCodeUsage.code_id == item.id, RedeemCodeUsage.request_id == data.request_id))).scalar_one_or_none()
        if previous:
            if previous.wx_user_id != data.wx_user_id or previous.wx_group_id != data.wx_group_id:
                raise HTTPException(409, "幂等请求身份不匹配")
            if previous.success and previous.result_json:
                return RedeemResult(**json.loads(previous.result_json))
            raise HTTPException(409, "该请求已处理")
    if item.max_uses > 1 and not data.request_id:
        raise HTTPException(400, "多次授权码兑换必须提供稳定的 request_id")
    now = datetime.now(timezone.utc)
    if item.status != "active":
        raise HTTPException(status_code=400, detail="授权码不可用")
    if item.valid_from and item.valid_from > now:
        raise HTTPException(status_code=400, detail="授权码尚未生效")
    if item.expires_at and item.expires_at < now:
        raise HTTPException(status_code=400, detail="授权码已过期")
    if item.used_count >= item.max_uses:
        raise HTTPException(status_code=400, detail="授权码已使用")

    user = await _get_or_create_user(db, data.wx_user_id, data.nickname)
    customer_id = item.customer_id
    group_id = None
    message = "兑换成功"

    if item.code_type == "diamonds":
        await grant_paid_diamonds(
            db, user, item.value, transaction_type="agent_code_purchase",
            reference_type="redeem_code", reference_id=item.id,
            description=f"代理商兑换码充值 {item.value} 钻石",
        )
        message = f"已到账 {item.value} 钻石"

    elif item.code_type == "group_license":
        if not data.wx_group_id:
            raise HTTPException(status_code=400, detail="群管理授权码必须在微信群中使用")
        if customer_id is None:
            customer = Customer(
                agent_id=item.agent_id, owner_user_id=user.id,
                name=(data.group_name or data.nickname or data.wx_user_id),
                plan_code="basic", license_status="active",
                license_started_at=now, license_expire_at=now + timedelta(days=(item.value if item.value > 0 else 365)), max_groups=3,
            )
            db.add(customer); await db.flush(); customer_id = customer.id; item.customer_id = customer_id
        else:
            customer = (await db.execute(select(Customer).where(Customer.id == customer_id)
                                        .with_for_update())).scalar_one_or_none()
            if customer is None:
                raise HTTPException(status_code=400, detail="授权码关联客户不存在")
            if customer.owner_user_id != user.id:
                raise HTTPException(status_code=403, detail="该管理授权码已预绑定其他购买者微信号")
            if customer.agent_id != item.agent_id:
                raise HTTPException(403, "授权码与客户代理归属不一致")
        if not customer.enabled or customer.license_status != "active" or (customer.license_expire_at and customer.license_expire_at <= now):
            raise HTTPException(403, "客户授权已暂停或过期")
        group = await _get_or_create_group(db, data.wx_group_id, data.group_name)
        group_id = group.id
        if group.customer_id not in (None, customer_id):
            raise HTTPException(status_code=409, detail="该群已绑定其他购买客户")

        existing_ownership_result = await db.execute(
            select(CustomerGroupOwnership).where(CustomerGroupOwnership.group_id == group.id)
        )
        existing_ownership = existing_ownership_result.scalar_one_or_none()
        if existing_ownership is not None and existing_ownership.customer_id != customer_id:
            raise HTTPException(409, "该群归属其他客户")
        if existing_ownership is None:
            customer_groups_result = await db.execute(
                select(CustomerGroupOwnership).where(CustomerGroupOwnership.customer_id == customer_id)
            )
            customer_group_count = len(customer_groups_result.scalars().all())
            owner_groups_result = await db.execute(
                select(CustomerGroupOwnership).where(CustomerGroupOwnership.owner_user_id == user.id)
            )
            owner_group_count = len(owner_groups_result.scalars().all())
            global_limit = await get_setting_int(db, "wechat_max_groups_per_account", 20)
            customer_limit = max(0, int(customer.max_groups or 0))
            if customer_group_count >= customer_limit:
                raise HTTPException(status_code=400, detail=f"当前客户套餐最多管理{customer_limit}个群")
            if owner_group_count >= global_limit:
                raise HTTPException(status_code=400, detail=f"当前微信号受风控限制，最多管理{global_limit}个群")

        group.customer_id = customer_id
        own_result = await db.execute(select(CustomerGroupOwnership).where(CustomerGroupOwnership.group_id == group.id))
        ownership = own_result.scalar_one_or_none()
        if ownership is None:
            db.add(CustomerGroupOwnership(
                customer_id=customer_id, group_id=group.id, owner_user_id=user.id,
                agent_id=item.agent_id, source_code_id=item.id,
            ))
        member_result = await db.execute(select(GroupMember).where(GroupMember.group_id == group.id, GroupMember.user_id == user.id))
        member = member_result.scalar_one_or_none()
        if member is None:
            db.add(GroupMember(customer_id=customer_id, group_id=group.id, user_id=user.id, member_role="owner"))
        else:
            member.customer_id = customer_id; member.member_role = "owner"; member.is_active = True
        message = "当前微信号已获得本群购买者/Owner管理权限"

    else:
        raise HTTPException(status_code=501, detail="该类型兑换码已预留，当前版本尚未开放兑换")

    item.used_count += 1
    if item.used_count >= item.max_uses:
        item.status = "redeemed"
    response = RedeemResult(success=True, code_type=item.code_type, message=message,
        user_id=user.id, customer_id=customer_id, group_id=group_id, value=item.value)
    db.add(RedeemCodeUsage(
        code_id=item.id, agent_id=item.agent_id, customer_id=customer_id,
        user_id=user.id, wx_user_id=data.wx_user_id, group_id=group_id,
        wx_group_id=data.wx_group_id, usage_type=item.code_type, value=item.value,
        success=True, request_id=data.request_id, use_number=item.used_count,
        result_json=response.model_dump_json(),
    ))
    await db.commit()
    return response


@router.get("/codes/{code_id}/reservation")
async def code_reservation(code_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(RedeemCode, code_id)
    if item is None:
        raise HTTPException(404, "授权码不存在")
    if item.code_type != "diamonds":
        raise HTTPException(400, "仅钻石码支持额度汇总")
    return reservation_summary(item)


async def _change_code_status(code_id, status, data, db, operator_name):
    op = f"code_{status}"
    if data.request_id:
        old = await _operation_once(db, op, "redeem_code", code_id, data.request_id)
        if old: return {"success": True, "code_id": code_id, "status": status, "idempotent": True}
    item = (await db.execute(select(RedeemCode).where(RedeemCode.id == code_id)
                            .with_for_update())).scalar_one_or_none()
    if item is None:
        raise HTTPException(404, "授权码不存在")
    if item.status == status:
        return {"success": True, "code_id": item.id, "status": item.status}
    if item.status not in {"active", "frozen"}:
        raise HTTPException(409, "当前授权码状态不允许该操作")
    if status == "active":
        released = (await db.execute(select(AgentDiamondQuotaTransaction.id).where(
            AgentDiamondQuotaTransaction.redeem_code_id == item.id,
            AgentDiamondQuotaTransaction.transaction_type == "code_release",
        ))).scalar_one_or_none()
        if released is not None:
            raise HTTPException(409, "该授权码已返还未用额度，不能解冻")
    before = item.status
    item.status = status
    db.add(_log(op, operator_name, "redeem_code", item.id, before, status, data.reason, data.request_id))
    await db.commit()
    return {"success": True, "code_id": item.id, "status": item.status}


@router.post("/codes/{code_id}/freeze")
async def freeze_code(code_id: int, data: CodeStatusRequest, db: AsyncSession = Depends(get_db),
                      operator_name: str = Depends(require_admin)):
    return await _change_code_status(code_id, "frozen", data, db, operator_name)


@router.post("/codes/{code_id}/unfreeze")
async def unfreeze_code(code_id: int, data: CodeStatusRequest, db: AsyncSession = Depends(get_db),
                        operator_name: str = Depends(require_admin)):
    return await _change_code_status(code_id, "active", data, db, operator_name)


@router.post("/codes/{code_id}/void")
async def void_code(code_id: int, data: CodeStatusRequest, db: AsyncSession = Depends(get_db),
                    operator_name: str = Depends(require_admin)):
    return await _change_code_status(code_id, "void", data, db, operator_name)


@router.post("/codes/{code_id}/refund")
async def refund_code_reservation(code_id: int, data: CodeRefundRequest,
                                  db: AsyncSession = Depends(get_db),
                                  operator_name: str = Depends(require_admin)):
    old_log = await _operation_once(db, "code_refund", "redeem_code", code_id, data.idempotency_key)
    if old_log:
        details = json.loads(old_log.details_json)
        return {"success": True, "code_id": code_id, "released": details["after"]["released"],
                "quota_before": details["before"]["quota"], "quota_after": details["after"]["quota"]}
    snapshot = (await db.execute(select(RedeemCode.id, RedeemCode.agent_id)
                                 .where(RedeemCode.id == code_id))).first()
    if snapshot is None:
        raise HTTPException(404, "授权码不存在")
    if snapshot.agent_id is None:
        raise HTTPException(400, "平台手工发行码没有可返还的代理额度")
    await lock_agent(db, snapshot.agent_id)
    item = (await db.execute(select(RedeemCode).where(RedeemCode.id == code_id)
                            .with_for_update().execution_options(populate_existing=True))).scalar_one()
    tx = await release_unused_diamond_quota(db, item, operator_name, data.reason, data.idempotency_key)
    db.add(_log("code_refund", operator_name, "redeem_code", item.id,
        {"quota": int(tx.quota_before)}, {"quota": int(tx.quota_after), "released": int(tx.amount)},
        data.reason, data.idempotency_key))
    await db.commit()
    return {"success": True, "code_id": item.id, "released": int(tx.amount),
            "quota_before": int(tx.quota_before), "quota_after": int(tx.quota_after)}


@router.get("/code-usages")
async def list_code_usages(page: int = 1, page_size: int = 20, agent_id: int | None = None,
        customer_id: int | None = None, wx_user_id: str | None = None, wx_group_id: str | None = None,
        usage_type: str | None = None, success: bool | None = None, started_at: datetime | None = None,
        ended_at: datetime | None = None, db: AsyncSession = Depends(get_db)):
    offset = _page(page, page_size); filters = []
    for column, value in ((RedeemCodeUsage.agent_id, agent_id), (RedeemCodeUsage.customer_id, customer_id),
        (RedeemCodeUsage.usage_type, usage_type), (RedeemCodeUsage.success, success)):
        if value is not None: filters.append(column == value)
    if wx_user_id: filters.append(RedeemCodeUsage.wx_user_id.ilike(f"%{wx_user_id.strip()}%"))
    if wx_group_id: filters.append(RedeemCodeUsage.wx_group_id.ilike(f"%{wx_group_id.strip()}%"))
    if started_at: filters.append(RedeemCodeUsage.used_at >= started_at)
    if ended_at: filters.append(RedeemCodeUsage.used_at <= ended_at)
    total = (await db.execute(select(func.count()).select_from(RedeemCodeUsage).where(*filters))).scalar_one()
    rows = (await db.execute(select(RedeemCodeUsage).where(*filters).order_by(RedeemCodeUsage.id.desc())
        .offset(offset).limit(page_size))).scalars().all()
    items = [{
        "id": r.id, "code_id": r.code_id, "agent_id": r.agent_id, "customer_id": r.customer_id,
        "user_id": r.user_id, "wx_user_id": r.wx_user_id, "group_id": r.group_id,
        "wx_group_id": r.wx_group_id, "usage_type": r.usage_type, "value": r.value,
        "success": r.success, "failure_reason": r.failure_reason, "used_at": r.used_at,
    } for r in rows]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/diamonds/{user_id}", response_model=DiamondBalanceResponse)
async def get_diamond_balance(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return DiamondBalanceResponse(user_id=user.id, paid_diamonds=int(user.paid_diamonds or 0), bonus_diamonds=int(user.bonus_diamonds or 0), total_diamonds=total_diamonds(user))


@router.get("/diamond-transactions")
async def list_diamond_transactions(page: int = 1, page_size: int = 20, user_id: int | None = None,
        wx_user_id: str | None = None, diamond_type: str | None = None, transaction_type: str | None = None,
        started_at: datetime | None = None, ended_at: datetime | None = None, db: AsyncSession = Depends(get_db)):
    offset = _page(page, page_size); filters = []
    for column, value in ((DiamondTransaction.user_id, user_id), (DiamondTransaction.diamond_type, diamond_type),
                          (DiamondTransaction.transaction_type, transaction_type)):
        if value is not None: filters.append(column == value)
    if started_at: filters.append(DiamondTransaction.created_at >= started_at)
    if ended_at: filters.append(DiamondTransaction.created_at <= ended_at)
    query = select(DiamondTransaction, User.wx_user_id).join(User, User.id == DiamondTransaction.user_id)
    count_query = select(func.count()).select_from(DiamondTransaction).join(User, User.id == DiamondTransaction.user_id)
    if wx_user_id:
        filters.append(User.wx_user_id.ilike(f"%{wx_user_id.strip()}%"))
    total = (await db.execute(count_query.where(*filters))).scalar_one()
    rows = (await db.execute(query.where(*filters).order_by(DiamondTransaction.id.desc())
        .offset(offset).limit(page_size))).all()
    items = [{
        "id": x.id, "user_id": x.user_id, "transaction_type": x.transaction_type,
        "wx_user_id": wx,
        "diamond_type": x.diamond_type, "amount": x.amount,
        "paid_before": x.paid_before, "paid_after": x.paid_after,
        "bonus_before": x.bonus_before, "bonus_after": x.bonus_after,
        "description": x.description, "created_at": x.created_at,
    } for x, wx in rows]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


async def _agent_ledger(model, page, page_size, agent_id, operation, actor, request_id, started_at, ended_at, db):
    offset = _page(page, page_size); filters = []
    for column, value in ((model.agent_id, agent_id), (model.transaction_type, operation),
                          (model.operator_name, actor), (model.idempotency_key, request_id)):
        if value is not None: filters.append(column == value)
    if started_at: filters.append(model.created_at >= started_at)
    if ended_at: filters.append(model.created_at <= ended_at)
    total = (await db.execute(select(func.count()).select_from(model).where(*filters))).scalar_one()
    rows = (await db.execute(select(model).where(*filters).order_by(model.id.desc()).offset(offset).limit(page_size))).scalars().all()
    items = []
    for x in rows:
        quota = model is AgentDiamondQuotaTransaction
        items.append({"id": x.id, "agent_id": x.agent_id, "operation": x.transaction_type,
            "change": int(x.amount), "before": int(x.quota_before if quota else x.balance_before),
            "after": int(x.quota_after if quota else x.balance_after), "actor": x.operator_name,
            "request_id": x.idempotency_key, "reason": x.reason if quota else x.description,
            "created_at": x.created_at})
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/agent-license-transactions")
async def list_agent_license_transactions(page: int = 1, page_size: int = 20, agent_id: int | None = None,
        operation: str | None = None, actor: str | None = None, request_id: str | None = None,
        started_at: datetime | None = None, ended_at: datetime | None = None, db: AsyncSession = Depends(get_db)):
    return await _agent_ledger(AgentLicenseTransaction, page, page_size, agent_id, operation, actor, request_id, started_at, ended_at, db)


@router.get("/agent-diamond-quota-transactions")
async def list_agent_quota_transactions(page: int = 1, page_size: int = 20, agent_id: int | None = None,
        operation: str | None = None, actor: str | None = None, request_id: str | None = None,
        started_at: datetime | None = None, ended_at: datetime | None = None, db: AsyncSession = Depends(get_db)):
    return await _agent_ledger(AgentDiamondQuotaTransaction, page, page_size, agent_id, operation, actor, request_id, started_at, ended_at, db)


@router.post("/asset-grants")
async def grant_asset(data: AssetGrantRequest, db: AsyncSession = Depends(get_db), operator_name: str = Depends(require_admin)):
    operator = await db.get(User, data.operator_user_id)
    target = await lock_user(db, data.target_user_id)
    if operator is None or target is None:
        raise HTTPException(status_code=404, detail="操作用户或目标用户不存在")
    customer = (await db.execute(select(Customer).where(Customer.id == data.customer_id)
                                .with_for_update())).scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if customer is None or not customer.enabled or customer.license_status != "active" or (
            customer.license_expire_at and customer.license_expire_at <= now):
        raise HTTPException(403, "客户授权无效")
    if data.group_id is not None:
        group = (await db.execute(select(Group).where(Group.id == data.group_id).with_for_update())).scalar_one_or_none()
        if group is None or group.customer_id != data.customer_id:
            raise HTTPException(403, "群不属于当前客户")
        member_result = await db.execute(select(GroupMember).where(GroupMember.customer_id == data.customer_id, GroupMember.group_id == data.group_id, GroupMember.user_id == data.operator_user_id, GroupMember.member_role.in_(["owner", "admin"]), GroupMember.is_active == True))
        if member_result.scalar_one_or_none() is None:
            raise HTTPException(status_code=403, detail="当前微信号没有该群管理权限")
        target_member = (await db.execute(select(GroupMember).where(GroupMember.customer_id == data.customer_id,
            GroupMember.group_id == data.group_id, GroupMember.user_id == data.target_user_id,
            GroupMember.is_active == True))).scalar_one_or_none()
        if target_member is None:
            raise HTTPException(403, "目标用户不是该群有效成员")
    elif customer.owner_user_id != data.operator_user_id:
        raise HTTPException(403, "未指定群时只允许客户 Owner 操作")
    if data.asset_type == "coins":
        before = int(target.coins or 0); target.coins = balance_after(before, data.amount); after = target.coins
        db.add(CoinTransaction(user_id=target.id, transaction_type="group_admin_grant",
            amount=data.amount, balance_before=before, balance_after=after,
            description=data.reason or "群管理员赠送蜗币"))
    elif data.asset_type == "bonus_diamonds":
        before = int(target.bonus_diamonds or 0)
        await grant_bonus_diamonds(db, target, data.amount, transaction_type="group_admin_grant", reference_type="customer", reference_id=data.customer_id, description=data.reason or "群管理员赠送奖励钻石")
        after = int(target.bonus_diamonds or 0)
    else:
        raise HTTPException(status_code=400, detail="只允许赠送蜗币或奖励钻石")
    grant = AdminAssetGrant(
        customer_id=data.customer_id, group_id=data.group_id, operator_user_id=data.operator_user_id,
        target_user_id=data.target_user_id, asset_type=data.asset_type, amount=data.amount,
        balance_before=before, balance_after=after, reason=data.reason,
    )
    db.add(grant); await db.flush()
    db.add(CommercialOperationLog(operation_type="asset_grant", operator_name=operator_name,
        target_type="admin_asset_grant", target_id=grant.id,
        details_json=json.dumps({"customer_id": data.customer_id, "group_id": data.group_id,
            "operator_user_id": data.operator_user_id, "target_user_id": data.target_user_id,
            "asset_type": data.asset_type, "amount": data.amount, "before": before, "after": after})))
    await db.commit(); await db.refresh(grant)
    return {"success": True, "grant_id": grant.id, "balance_before": before, "balance_after": after}


@router.get("/membership/plans", response_model=list[MembershipPlanResponse])
async def list_membership_plans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MembershipPlan).order_by(MembershipPlan.sort_order.asc(), MembershipPlan.id.asc()))
    return result.scalars().all()


@router.post("/membership/plans", response_model=MembershipPlanResponse)
async def create_membership_plan(data: MembershipPlanCreate, db: AsyncSession = Depends(get_db)):
    exists = await db.execute(select(MembershipPlan).where(MembershipPlan.code == data.code.strip().lower()))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="会员方案编码已存在")
    item = MembershipPlan(code=data.code.strip().lower(), name=data.name.strip(), member_level=data.member_level.strip().lower(), enabled=data.enabled, sort_order=data.sort_order)
    db.add(item); await db.commit(); await db.refresh(item); return item


@router.get("/membership/products", response_model=list[MembershipProductResponse])
async def list_membership_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MembershipProduct).order_by(MembershipProduct.sort_order.asc(), MembershipProduct.id.asc()))
    return result.scalars().all()


@router.post("/membership/products", response_model=MembershipProductResponse)
async def create_membership_product(data: MembershipProductCreate, db: AsyncSession = Depends(get_db)):
    plan = await db.get(MembershipPlan, data.plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="会员方案不存在")
    if data.bonus_grant_mode not in {"immediate", "monthly"}:
        raise HTTPException(status_code=400, detail="赠钻模式只支持 immediate 或 monthly")
    item = MembershipProduct(**data.model_dump())
    db.add(item); await db.commit(); await db.refresh(item); return item


@router.put("/membership/products/{product_id}", response_model=MembershipProductResponse)
async def update_membership_product(product_id: int, data: MembershipProductUpdate,
        db: AsyncSession = Depends(get_db), operator_name: str = Depends(require_admin)):
    old = await _operation_once(db, "membership_product_update", "membership_product", product_id, data.request_id)
    if old:
        item = await db.get(MembershipProduct, product_id)
        if item is None: raise HTTPException(404, "会员商品不存在")
        return item
    item = (await db.execute(select(MembershipProduct).where(MembershipProduct.id == product_id).with_for_update())).scalar_one_or_none()
    if item is None: raise HTTPException(404, "会员商品不存在")
    if await db.get(MembershipPlan, data.plan_id) is None: raise HTTPException(404, "会员方案不存在")
    if data.bonus_grant_mode not in {"immediate", "monthly"}: raise HTTPException(400, "赠钻模式无效")
    before = {k: getattr(item, k) for k in MembershipProductCreate.model_fields}
    values = data.model_dump(exclude={"reason", "request_id"})
    for key, value in values.items(): setattr(item, key, value)
    after = {k: getattr(item, k) for k in MembershipProductCreate.model_fields}
    db.add(_log("membership_product_update", operator_name, "membership_product", item.id,
        before, after, data.reason, data.request_id))
    await db.commit(); await db.refresh(item); return item


@router.post("/membership/purchase-diamonds")
async def purchase_membership_with_diamonds(data: MembershipDiamondPurchase, db: AsyncSession = Depends(get_db)):
    user_result = await db.execute(select(User).where(User.id == data.user_id).with_for_update())
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    product = await db.get(MembershipProduct, data.product_id)
    if product is None or not product.enabled:
        raise HTTPException(status_code=404, detail="会员商品不存在或已下架")
    plan = await db.get(MembershipPlan, product.plan_id)
    if plan is None or not plan.enabled:
        raise HTTPException(status_code=400, detail="会员方案不可用")
    now = datetime.now(timezone.utc)
    if product.diamond_price > 0:
        await spend_diamonds(db, user, product.diamond_price, transaction_type="membership_purchase", reference_type="membership_product", reference_id=product.id, description=f"购买会员：{product.name}")
    current_expire = user.member_expire_at if user.member_expire_at and user.member_expire_at > now else now
    expires = current_expire + timedelta(days=product.duration_days)
    user.member_level = plan.member_level
    if not user.member_started_at or user.member_level == "normal":
        user.member_started_at = now
    user.member_expire_at = expires
    membership = UserMembership(user_id=user.id, plan_id=plan.id, product_id=product.id, status="active", started_at=now, expires_at=expires, next_bonus_at=(now + timedelta(days=30) if product.bonus_grant_mode == "monthly" and product.bonus_diamonds > 0 else None), source_type="diamond_purchase")
    db.add(membership); await db.flush()
    if product.bonus_diamonds > 0 and product.bonus_grant_mode == "immediate":
        await grant_bonus_diamonds(db, user, product.bonus_diamonds, transaction_type="membership_grant", reference_type="user_membership", reference_id=membership.id, description=f"{product.name}会员赠钻")
    await db.commit()
    return {"success": True, "membership_id": membership.id, "member_level": user.member_level, "expires_at": user.member_expire_at, "paid_diamonds": user.paid_diamonds, "bonus_diamonds": user.bonus_diamonds}


@router.post("/entitlements/purchase")
async def purchase_entitlement(data: EntitlementPurchaseRequest, db: AsyncSession = Depends(get_db)):
    mapping = {
        "extra_partner_slots": ("partner_slot_diamond_price", "max_extra_partner_slots", "伴侣槽"),
        "extra_baby_slots": ("baby_slot_diamond_price", "max_extra_baby_slots", "宝宝槽"),
    }
    if data.entitlement_key not in mapping:
        raise HTTPException(status_code=400, detail="不支持的扩容权益")
    price_key, max_key, label = mapping[data.entitlement_key]
    user_result = await db.execute(select(User).where(User.id == data.user_id).with_for_update())
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    unit_price = await get_setting_int(db, price_key, 500 if data.entitlement_key == "extra_partner_slots" else 200)
    max_qty = await get_setting_int(db, max_key, 3 if data.entitlement_key == "extra_partner_slots" else 6)
    current = await get_entitlement_quantity(db, user.id, data.entitlement_key)
    if current + data.quantity > max_qty:
        raise HTTPException(status_code=400, detail=f"{label}最多可额外购买{max_qty}个，当前已有{current}个")
    total_price = unit_price * data.quantity
    await spend_diamonds(db, user, total_price, transaction_type="entitlement_purchase", reference_type=data.entitlement_key, description=f"购买{label} × {data.quantity}")
    item = await add_entitlement(db, user.id, data.entitlement_key, data.quantity, source_type="diamond_purchase")
    await db.commit()
    return {"success": True, "entitlement_key": data.entitlement_key, "quantity": item.quantity, "spent_diamonds": total_price, "paid_diamonds": user.paid_diamonds, "bonus_diamonds": user.bonus_diamonds}


@router.get("/entitlements/{user_id}")
async def get_user_entitlements(user_id: int, db: AsyncSession = Depends(get_db)):
    return {
        "user_id": user_id,
        "extra_partner_slots": await get_entitlement_quantity(db, user_id, "extra_partner_slots"),
        "extra_baby_slots": await get_entitlement_quantity(db, user_id, "extra_baby_slots"),
    }
