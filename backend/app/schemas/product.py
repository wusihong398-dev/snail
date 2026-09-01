from datetime import datetime

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=128
    )

    product_type: str = "member"

    member_level: str | None = None

    member_days: int | None = None

    price_cents: int = 0

    coin_price: int = 0

    enabled: bool = True

    sort_order: int = 0

    description: str | None = None


class ProductUpdate(BaseModel):

    name: str | None = None

    product_type: str | None = None

    member_level: str | None = None

    member_days: int | None = None

    price_cents: int | None = None

    coin_price: int | None = None

    enabled: bool | None = None

    sort_order: int | None = None

    description: str | None = None


class ProductResponse(BaseModel):

    id: int

    name: str

    product_type: str

    member_level: str | None = None

    member_days: int | None = None

    price_cents: int = 0

    coin_price: int = 0

    enabled: bool = True

    sort_order: int = 0

    description: str | None = None

    created_at: datetime | None = None


    class Config:

        from_attributes = True
