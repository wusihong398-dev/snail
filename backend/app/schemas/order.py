from datetime import datetime

from pydantic import BaseModel


class CoinPurchaseRequest(BaseModel):

    user_id: int

    product_id: int


class OrderResponse(BaseModel):

    id: int

    order_no: str

    user_id: int

    product_id: int

    product_name: str

    product_type: str

    member_level: str | None = None

    member_days: int | None = None

    payment_method: str

    amount_cents: int

    coin_amount: int

    status: str

    created_at: datetime | None = None

    paid_at: datetime | None = None

    class Config:
        from_attributes = True


class CoinTransactionResponse(BaseModel):

    id: int

    user_id: int

    transaction_type: str

    amount: int

    balance_before: int

    balance_after: int

    order_id: int | None = None

    description: str | None = None

    created_at: datetime | None = None

    class Config:
        from_attributes = True
