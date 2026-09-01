from datetime import datetime

from pydantic import BaseModel


class GiftProductCreate(BaseModel):

    product_id: int

    icon_url: str | None = None

    rarity: str = "normal"

    exp_reward: int = 0

    intimacy_reward: int = 0


class GiftProductUpdate(BaseModel):

    icon_url: str | None = None

    rarity: str | None = None

    exp_reward: int | None = None

    intimacy_reward: int | None = None


class GiftProductResponse(BaseModel):

    id: int

    product_id: int

    icon_url: str | None = None

    rarity: str

    exp_reward: int

    intimacy_reward: int

    created_at: datetime | None = None

    class Config:
        from_attributes = True


class GiftSendRequest(BaseModel):

    sender_user_id: int

    receiver_user_id: int

    product_id: int

    quantity: int = 1


class GiftRecordResponse(BaseModel):

    id: int

    order_id: int

    sender_user_id: int

    receiver_user_id: int

    product_id: int

    gift_name: str

    quantity: int

    coin_amount: int

    exp_reward: int

    intimacy_reward: int

    created_at: datetime | None = None

    class Config:
        from_attributes = True
