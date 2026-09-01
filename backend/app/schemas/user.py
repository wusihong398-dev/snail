from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):

    wx_user_id: str = Field(
        min_length=1,
        max_length=128
    )

    nickname: str = Field(
        default="",
        max_length=64
    )

    avatar: str = Field(
        default="",
        max_length=255
    )


class UserUpdate(BaseModel):

    nickname: str | None = Field(
        default=None,
        max_length=64
    )

    avatar: str | None = Field(
        default=None,
        max_length=255
    )

    level: int | None = None

    coins: int | None = None

    experience: int | None = None

    is_active: bool | None = None


class UserCoinsUpdate(BaseModel):
    amount: int


class UserExperienceUpdate(BaseModel):
    amount: int


class UserMembershipUpdate(BaseModel):

    member_level: str

    days: int | None = None


class UserResponse(BaseModel):

    id: int

    wx_user_id: str

    nickname: str | None = ""

    avatar: str | None = ""

    level: int = 1

    coins: int = 0

    paid_diamonds: int = 0

    bonus_diamonds: int = 0

    experience: int = 0

    is_active: bool = True

    member_level: str = "normal"

    member_started_at: datetime | None = None

    member_expire_at: datetime | None = None

    created_at: datetime | None = None


    class Config:
        from_attributes = True
