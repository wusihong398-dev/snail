from datetime import datetime
from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    name: str
    agent_code: str
    agent_type: str = "commission"
    commission_rate: float = 0
    license_balance: int = 0
    diamond_quota: int = 0


class AgentResponse(AgentCreate):
    id: int
    enabled: bool
    parent_agent_id: int | None = None
    created_at: datetime | None = None
    class Config:
        from_attributes = True


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


class RedeemCodeCreate(BaseModel):
    code_type: str
    agent_id: int | None = None
    customer_id: int | None = None
    value: int = 0
    expires_hours: int = Field(default=168, ge=1, le=87600)
    max_uses: int = Field(default=1, ge=1, le=1000)
    created_by: str | None = None


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
    created_by: str | None = None
    created_at: datetime | None = None
    class Config:
        from_attributes = True


class RedeemRequest(BaseModel):
    code: str
    wx_user_id: str
    wx_group_id: str | None = None
    nickname: str | None = None
    group_name: str | None = None


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


class MembershipDiamondPurchase(BaseModel):
    user_id: int
    product_id: int


class EntitlementPurchaseRequest(BaseModel):
    user_id: int
    entitlement_key: str
    quantity: int = Field(default=1, ge=1, le=100)
