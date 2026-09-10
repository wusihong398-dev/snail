from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    agent_code: str = Field(min_length=1, max_length=64)
    agent_type: Literal["commission", "prepaid", "hybrid"] = "commission"
    commission_rate: float = Field(default=0, ge=0, le=1)
    license_balance: int = Field(default=0, ge=0, le=2147483647)
    diamond_quota: int = Field(default=0, ge=0, le=2147483647)


class AgentResponse(AgentCreate):
    id: int
    enabled: bool
    parent_agent_id: int | None = None
    created_at: datetime | None = None
    class Config:
        from_attributes = True


class AgentUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    agent_type: Literal["commission", "prepaid", "hybrid"]
    commission_rate: float = Field(ge=0, le=1)
    reason: str = Field(min_length=1, max_length=255)
    request_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")


class BalanceAdjustment(BaseModel):
    change: int = Field(ge=-2147483647, le=2147483647)
    reason: str = Field(min_length=1, max_length=255)
    request_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")


class OperationRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=255)
    request_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")


class CustomerResponse(BaseModel):
    id: int
    agent_id: int | None = None
    owner_user_id: int
    name: str | None = None
    plan_code: str
    license_status: str
    license_started_at: datetime | None = None
    license_expire_at: datetime | None = None
    max_groups: int
    enabled: bool
    created_at: datetime | None = None
    class Config:
        from_attributes = True


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=128)
    agent_id: int | None = None
    plan_code: str = Field(min_length=1, max_length=64)
    max_groups: int = Field(ge=0, le=2147483647)
    reason: str = Field(min_length=1, max_length=255)
    request_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")


class CustomerRenewRequest(BaseModel):
    duration_days: int = Field(ge=1, le=36500)
    reason: str = Field(min_length=1, max_length=255)
    request_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")


class RedeemCodeCreate(BaseModel):
    code_type: str
    agent_id: int | None = None
    customer_id: int | None = None
    value: int = Field(default=0, ge=0, le=2147483647)
    expires_hours: int = Field(default=168, ge=1, le=87600)
    max_uses: int = Field(default=1, ge=1, le=1000)
    created_by: str | None = None
    request_id: str | None = Field(default=None, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")


class RedeemCodeGenerated(BaseModel):
    id: int
    code: str
    code_type: str
    agent_id: int | None = None
    customer_id: int | None = None
    value: int
    expires_at: datetime | None = None
    max_uses: int


class RedeemCodeListItem(BaseModel):
    id: int
    code_prefix: str
    code_type: str
    agent_id: int | None = None
    customer_id: int | None = None
    value: int
    valid_from: datetime | None = None
    expires_at: datetime | None = None
    max_uses: int
    used_count: int
    status: str
    reservation_source: str | None = None
    reserved_total: int | None = None
    created_by: str | None = None
    created_at: datetime | None = None
    class Config:
        from_attributes = True


class RedeemRequest(BaseModel):
    code: str
    wx_user_id: str = Field(min_length=1, max_length=128)
    wx_group_id: str | None = Field(default=None, min_length=1, max_length=128)
    nickname: str | None = None
    group_name: str | None = None
    request_id: str | None = Field(default=None, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")


class CodeStatusRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=255)
    request_id: str | None = Field(default=None, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")


class CodeRefundRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=255)
    idempotency_key: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")


class RedeemResult(BaseModel):
    success: bool
    code_type: str
    message: str
    user_id: int | None = None
    customer_id: int | None = None
    group_id: int | None = None
    value: int = 0


class AssetGrantRequest(BaseModel):
    customer_id: int
    group_id: int | None = None
    operator_user_id: int
    target_user_id: int
    asset_type: str
    amount: int = Field(gt=0)
    reason: str | None = None


class DiamondBalanceResponse(BaseModel):
    user_id: int
    paid_diamonds: int
    bonus_diamonds: int
    total_diamonds: int


class MembershipPlanCreate(BaseModel):
    code: str
    name: str
    member_level: str
    enabled: bool = True
    sort_order: int = 0


class MembershipPlanResponse(MembershipPlanCreate):
    id: int
    created_at: datetime | None = None
    class Config:
        from_attributes = True


class MembershipProductCreate(BaseModel):
    plan_id: int
    name: str
    duration_days: int = Field(gt=0)
    price_cents: int = Field(default=0, ge=0)
    diamond_price: int = Field(default=0, ge=0)
    bonus_diamonds: int = Field(default=0, ge=0)
    bonus_grant_mode: str = "immediate"
    enabled: bool = True
    sort_order: int = 0


class MembershipProductResponse(MembershipProductCreate):
    id: int
    created_at: datetime | None = None
    class Config:
        from_attributes = True


class MembershipProductUpdate(MembershipProductCreate):
    reason: str = Field(min_length=1, max_length=255)
    request_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")


class MembershipDiamondPurchase(BaseModel):
    user_id: int
    product_id: int


class EntitlementPurchaseRequest(BaseModel):
    user_id: int
    entitlement_key: str
    quantity: int = Field(default=1, ge=1, le=100)
