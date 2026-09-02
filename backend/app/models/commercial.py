from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Numeric, Text
from sqlalchemy.sql import func
from app.database import Base


class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    agent_code = Column(String(64), unique=True, nullable=False)
    agent_type = Column(String(30), default="commission", nullable=False)
    commission_rate = Column(Numeric(8, 4), default=0, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    parent_agent_id = Column(Integer, nullable=True)
    license_balance = Column(Integer, default=0, nullable=False)
    diamond_quota = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, nullable=True)
    owner_user_id = Column(Integer, nullable=False)
    name = Column(String(128), nullable=True)
    plan_code = Column(String(64), default="basic", nullable=False)
    license_status = Column(String(30), default="active", nullable=False)
    license_started_at = Column(DateTime(timezone=True), nullable=True)
    license_expire_at = Column(DateTime(timezone=True), nullable=True)
    max_groups = Column(Integer, default=3, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CustomerGroupOwnership(Base):
    __tablename__ = "customer_group_ownerships"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, nullable=False)
    group_id = Column(Integer, nullable=False)
    owner_user_id = Column(Integer, nullable=False)
    agent_id = Column(Integer, nullable=True)
    source_code_id = Column(Integer, nullable=True)
    activated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class GroupMember(Base):
    __tablename__ = "group_members"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, nullable=False)
    group_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    group_nickname = Column(String(128), nullable=True)
    member_role = Column(String(30), default="member", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class GroupAdminPermission(Base):
    __tablename__ = "group_admin_permissions"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, nullable=False)
    group_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    permission_key = Column(String(80), nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    granted_by_user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class RedeemCode(Base):
    __tablename__ = "redeem_codes"
    id = Column(Integer, primary_key=True)
    code_prefix = Column(String(32), nullable=False)
    code_hash = Column(String(128), unique=True, nullable=False)
    code_type = Column(String(40), nullable=False)
    agent_id = Column(Integer, nullable=True)
    customer_id = Column(Integer, nullable=True)
    product_id = Column(Integer, nullable=True)
    value = Column(Integer, default=0, nullable=False)
    metadata_json = Column(Text, nullable=True)
    valid_from = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    max_uses = Column(Integer, default=1, nullable=False)
    used_count = Column(Integer, default=0, nullable=False)
    status = Column(String(30), default="active", nullable=False)
    created_by = Column(String(80), nullable=True)
    request_id = Column(String(128), nullable=True)
    reservation_source = Column(String(30), nullable=True)
    reserved_total = Column(BigInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class RedeemCodeUsage(Base):
    __tablename__ = "redeem_code_usages"
    id = Column(Integer, primary_key=True)
    code_id = Column(Integer, nullable=False)
    agent_id = Column(Integer, nullable=True)
    customer_id = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=True)
    wx_user_id = Column(String(128), nullable=True)
    group_id = Column(Integer, nullable=True)
    wx_group_id = Column(String(128), nullable=True)
    usage_type = Column(String(40), nullable=False)
    value = Column(Integer, default=0, nullable=False)
    success = Column(Boolean, default=False, nullable=False)
    failure_reason = Column(String(255), nullable=True)
    request_id = Column(String(128), nullable=True)
    use_number = Column(Integer, nullable=True)
    result_json = Column(Text, nullable=True)
    used_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AdminAssetGrant(Base):
    __tablename__ = "admin_asset_grants"
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, nullable=True)
    customer_id = Column(Integer, nullable=False)
    group_id = Column(Integer, nullable=True)
    operator_user_id = Column(Integer, nullable=False)
    target_user_id = Column(Integer, nullable=False)
    asset_type = Column(String(40), nullable=False)
    amount = Column(Integer, nullable=False)
    balance_before = Column(Integer, default=0, nullable=False)
    balance_after = Column(Integer, default=0, nullable=False)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class MembershipPlan(Base):
    __tablename__ = "membership_plans"
    id = Column(Integer, primary_key=True)
    code = Column(String(40), unique=True, nullable=False)
    name = Column(String(80), nullable=False)
    member_level = Column(String(30), default="normal", nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class MembershipPlanEntitlement(Base):
    __tablename__ = "membership_plan_entitlements"
    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, nullable=False)
    entitlement_key = Column(String(100), nullable=False)
    entitlement_value = Column(String(100), nullable=False)


class MembershipProduct(Base):
    __tablename__ = "membership_products"
    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    duration_days = Column(Integer, nullable=False)
    price_cents = Column(Integer, default=0, nullable=False)
    diamond_price = Column(Integer, default=0, nullable=False)
    bonus_diamonds = Column(Integer, default=0, nullable=False)
    bonus_grant_mode = Column(String(20), default="immediate", nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserMembership(Base):
    __tablename__ = "user_memberships"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    plan_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=True)
    status = Column(String(30), default="active", nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    next_bonus_at = Column(DateTime(timezone=True), nullable=True)
    source_type = Column(String(30), default="purchase", nullable=False)
    source_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
