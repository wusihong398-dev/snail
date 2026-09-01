from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
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
from app.schemas.commercial import (
    AgentCreate, AgentResponse, CustomerResponse,
    RedeemCodeCreate, RedeemCodeGenerated, RedeemCodeListItem,
    RedeemRequest, RedeemResult, AssetGrantRequest, DiamondBalanceResponse,
    MembershipPlanCreate, MembershipPlanResponse, MembershipProductCreate,
    MembershipProductResponse, MembershipDiamondPurchase, EntitlementPurchaseRequest,
)
from app.services.redeem_codes import generate_code, hash_code
from app.services.diamonds import add_paid_diamonds, add_bonus_diamonds, spend_diamonds, total_diamonds
from app.auth.dependencies import require_admin
from app.services.entitlements import get_entitlement_quantity, add_entitlement
from app.services.system_settings import get_setting_int

router = APIRouter(prefix="/commercial", tags=["商业授权与代理"], dependencies=[Depends(require_admin)])
public_router = APIRouter(prefix="/commercial", tags=["授权码兑换"])

SUPPORTED_CODE_TYPES = {"group_license", "diamonds", "membership", "partner_slot", "baby_slot"}


@router.get("/agents", response_model=list[AgentResponse])
async def list_agents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).order_by(Agent.id.desc()))
    return result.scalars().all()


@router.post("/agents", response_model=AgentResponse)
async def create_agent(data: AgentCreate, db: AsyncSession = Depends(get_db)):
    exists = await db.execute(select(Agent).where(Agent.agent_code == data.agent_code.strip()))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="代理商编码已存在")
    agent = Agent(
        name=data.name.strip(), agent_code=data.agent_code.strip(), agent_type=data.agent_type,
        commission_rate=data.commission_rate, license_balance=data.license_balance,
        diamond_quota=data.diamond_quota,
    )
    db.add(agent)
    await db.commit(); await db.refresh(agent)
    return agent


@router.get("/customers", response_model=list[CustomerResponse])
async def list_customers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).order_by(Customer.id.desc()))
    return result.scalars().all()


@router.get("/codes", response_model=list[RedeemCodeListItem])
async def list_codes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RedeemCode).order_by(RedeemCode.id.desc()).limit(1000))
    return result.scalars().all()


@router.post("/codes", response_model=RedeemCodeGenerated)
async def create_code(data: RedeemCodeCreate, db: AsyncSession = Depends(get_db)):
    if data.code_type not in SUPPORTED_CODE_TYPES:
        raise HTTPException(status_code=400, detail="不支持的授权码类型")
    agent = None
    if data.agent_id is not None:
        agent = await db.get(Agent, data.agent_id)
        if agent is None or not agent.enabled:
            raise HTTPException(status_code=404, detail="代理商不存在或已停用")
        if data.code_type == "group_license" and agent.agent_type in {"prepaid", "hybrid"}:
            if agent.license_balance <= 0:
                raise HTTPException(status_code=400, detail="代理商授权库存不足")
            agent.license_balance -= 1
        if data.code_type == "diamonds" and agent.agent_type in {"prepaid", "hybrid"}:
            if data.value <= 0:
                raise HTTPException(status_code=400, detail="钻石兑换码数量必须大于0")
            if agent.diamond_quota < data.value:
                raise HTTPException(status_code=400, detail="代理商钻石销售额度不足")
            agent.diamond_quota -= data.value
    if data.code_type == "diamonds" and data.value <= 0:
        raise HTTPException(status_code=400, detail="钻石兑换码数量必须大于0")
    code, prefix, digest = generate_code(data.code_type)
    now = datetime.now(timezone.utc)
    item = RedeemCode(
        code_prefix=prefix, code_hash=digest, code_type=data.code_type,
        agent_id=data.agent_id, customer_id=data.customer_id, value=data.value,
        valid_from=now, expires_at=now + timedelta(hours=data.expires_hours),
        max_uses=data.max_uses, used_count=0, status="active", created_by=data.created_by,
    )
    db.add(item); await db.commit(); await db.refresh(item)
    return RedeemCodeGenerated(
        id=item.id, code=code, code_type=item.code_type, agent_id=item.agent_id,
        customer_id=item.customer_id, value=item.value, expires_at=item.expires_at,
        max_uses=item.max_uses,
    )


async def _get_or_create_user(db: AsyncSession, wx_user_id: str, nickname: str | None):
    result = await db.execute(select(User).where(User.wx_user_id == wx_user_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(wx_user_id=wx_user_id, nickname=nickname or "", coins=0, experience=0)
        db.add(user); await db.flush()
    elif nickname and not user.nickname:
        user.nickname = nickname
    return user


async def _get_or_create_group(db: AsyncSession, wx_group_id: str, group_name: str | None):
    result = await db.execute(select(Group).where(Group.wx_group_id == wx_group_id))
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
    result = await db.execute(select(RedeemCode).where(RedeemCode.code_hash == digest).with_for_update())
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="授权码不存在")
    now = datetime.now(timezone.utc)
    if item.status != "active":
        raise HTTPException(status_code=400, detail="授权码不可用")
    if item.valid_from and item.valid_from > now:
        raise HTTPException(status_code=400, detail="授权码尚未生效")
    if item.expires_at and item.expires_at < now:
        item.status = "expired"; await db.commit()
        raise HTTPException(status_code=400, detail="授权码已过期")
    if item.used_count >= item.max_uses:
        item.status = "redeemed"; await db.commit()
        raise HTTPException(status_code=400, detail="授权码已使用")

    user = await _get_or_create_user(db, data.wx_user_id, data.nickname)
    customer_id = item.customer_id
    group_id = None
    message = "兑换成功"

    if item.code_type == "diamonds":
        await add_paid_diamonds(
            db, user, item.value, transaction_type="agent_code_purchase",
            reference_type="redeem_code", reference_id=item.id,
            description=f"代理商兑换码充值 {item.value} 钻石",
        )
        message = f"已到账 {item.value} 钻石"

    elif item.code_type == "group_license":
        if not data.wx_group_id:
            raise HTTPException(status_code=400, detail="群管理授权码必须在微信群中使用")
        group = await _get_or_create_group(db, data.wx_group_id, data.group_name)
        group_id = group.id
        if customer_id is None:
            customer = Customer(
                agent_id=item.agent_id, owner_user_id=user.id,
                name=(data.group_name or data.nickname or data.wx_user_id),
                plan_code="basic", license_status="active",
                license_started_at=now, license_expire_at=now + timedelta(days=(item.value if item.value > 0 else 365)), max_groups=3,
            )
            db.add(customer); await db.flush(); customer_id = customer.id; item.customer_id = customer_id
        else:
            customer = await db.get(Customer, customer_id)
            if customer is None:
                raise HTTPException(status_code=400, detail="授权码关联客户不存在")
            if customer.owner_user_id != user.id:
                raise HTTPException(status_code=403, detail="该管理授权码已预绑定其他购买者微信号")
        if group.customer_id not in (None, customer_id):
            raise HTTPException(status_code=409, detail="该群已绑定其他购买客户")

        existing_ownership_result = await db.execute(
            select(CustomerGroupOwnership).where(CustomerGroupOwnership.group_id == group.id)
        )
        existing_ownership = existing_ownership_result.scalar_one_or_none()
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
    db.add(RedeemCodeUsage(
        code_id=item.id, agent_id=item.agent_id, customer_id=customer_id,
        user_id=user.id, wx_user_id=data.wx_user_id, group_id=group_id,
        wx_group_id=data.wx_group_id, usage_type=item.code_type, value=item.value,
        success=True,
    ))
    await db.commit()
    return RedeemResult(success=True, code_type=item.code_type, message=message, user_id=user.id, customer_id=customer_id, group_id=group_id, value=item.value)


@router.get("/code-usages")
async def list_code_usages(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RedeemCodeUsage).order_by(RedeemCodeUsage.id.desc()).limit(1000))
    rows = result.scalars().all()
    return [{
        "id": r.id, "code_id": r.code_id, "agent_id": r.agent_id, "customer_id": r.customer_id,
        "user_id": r.user_id, "wx_user_id": r.wx_user_id, "group_id": r.group_id,
        "wx_group_id": r.wx_group_id, "usage_type": r.usage_type, "value": r.value,
        "success": r.success, "failure_reason": r.failure_reason, "used_at": r.used_at,
    } for r in rows]


@router.get("/diamonds/{user_id}", response_model=DiamondBalanceResponse)
async def get_diamond_balance(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return DiamondBalanceResponse(user_id=user.id, paid_diamonds=int(user.paid_diamonds or 0), bonus_diamonds=int(user.bonus_diamonds or 0), total_diamonds=total_diamonds(user))


@router.get("/diamond-transactions")
async def list_diamond_transactions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DiamondTransaction).order_by(DiamondTransaction.id.desc()).limit(1000))
    rows = result.scalars().all()
    return [{
        "id": x.id, "user_id": x.user_id, "transaction_type": x.transaction_type,
        "diamond_type": x.diamond_type, "amount": x.amount,
        "paid_before": x.paid_before, "paid_after": x.paid_after,
        "bonus_before": x.bonus_before, "bonus_after": x.bonus_after,
        "description": x.description, "created_at": x.created_at,
    } for x in rows]


@router.post("/asset-grants")
async def grant_asset(data: AssetGrantRequest, db: AsyncSession = Depends(get_db)):
    operator = await db.get(User, data.operator_user_id)
    target = await db.get(User, data.target_user_id)
    if operator is None or target is None:
        raise HTTPException(status_code=404, detail="操作用户或目标用户不存在")
    if data.group_id is not None:
        member_result = await db.execute(select(GroupMember).where(GroupMember.group_id == data.group_id, GroupMember.user_id == data.operator_user_id, GroupMember.member_role.in_(["owner", "admin"]), GroupMember.is_active == True))
        if member_result.scalar_one_or_none() is None:
            raise HTTPException(status_code=403, detail="当前微信号没有该群管理权限")
    if data.asset_type == "coins":
        before = int(target.coins or 0); target.coins = before + data.amount; after = target.coins
    elif data.asset_type == "bonus_diamonds":
        before = int(target.bonus_diamonds or 0)
        await add_bonus_diamonds(db, target, data.amount, transaction_type="group_admin_grant", reference_type="customer", reference_id=data.customer_id, description=data.reason or "群管理员赠送奖励钻石")
        after = int(target.bonus_diamonds or 0)
    else:
        raise HTTPException(status_code=400, detail="只允许赠送蜗币或奖励钻石")
    grant = AdminAssetGrant(
        customer_id=data.customer_id, group_id=data.group_id, operator_user_id=data.operator_user_id,
        target_user_id=data.target_user_id, asset_type=data.asset_type, amount=data.amount,
        balance_before=before, balance_after=after, reason=data.reason,
    )
    db.add(grant); await db.commit(); await db.refresh(grant)
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
        await add_bonus_diamonds(db, user, product.bonus_diamonds, transaction_type="membership_grant", reference_type="user_membership", reference_id=membership.id, description=f"{product.name}会员赠钻")
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
