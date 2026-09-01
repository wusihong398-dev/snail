from datetime import datetime

from pydantic import BaseModel, Field


class WechatAccountCreate(BaseModel):
    nickname: str | None = Field(
        default=None,
        max_length=64
    )

    wxid: str | None = Field(
        default=None,
        max_length=128
    )

    online: bool = False

    customer_id: int | None = None


class WechatAccountUpdate(BaseModel):
    nickname: str | None = Field(
        default=None,
        max_length=64
    )

    wxid: str | None = Field(
        default=None,
        max_length=128
    )

    online: bool | None = None

    customer_id: int | None = None


class WechatOnlineUpdate(BaseModel):
    online: bool


class WechatAccountResponse(BaseModel):
    id: int
    nickname: str | None = None
    wxid: str | None = None
    online: bool | None = False
    customer_id: int | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True
