from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime
)

from sqlalchemy.sql import func

from app.database import Base


class ShopOrder(Base):

    __tablename__ = "shop_orders"

    id = Column(
        Integer,
        primary_key=True
    )

    order_no = Column(
        String(64),
        unique=True,
        nullable=False
    )

    user_id = Column(
        Integer,
        nullable=False
    )

    product_id = Column(
        Integer,
        nullable=False
    )

    product_name = Column(
        String(128),
        nullable=False
    )

    product_type = Column(
        String(30),
        nullable=False
    )

    member_level = Column(
        String(30),
        nullable=True
    )

    member_days = Column(
        Integer,
        nullable=True
    )

    payment_method = Column(
        String(30),
        default="coins",
        nullable=False
    )

    amount_cents = Column(
        Integer,
        default=0,
        nullable=False
    )

    coin_amount = Column(
        Integer,
        default=0,
        nullable=False
    )

    status = Column(
        String(30),
        default="pending",
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    paid_at = Column(
        DateTime(timezone=True),
        nullable=True
    )


class CoinTransaction(Base):

    __tablename__ = "coin_transactions"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        nullable=False
    )

    transaction_type = Column(
        String(30),
        nullable=False
    )

    amount = Column(
        Integer,
        nullable=False
    )

    balance_before = Column(
        Integer,
        nullable=False
    )

    balance_after = Column(
        Integer,
        nullable=False
    )

    order_id = Column(
        Integer,
        nullable=True
    )

    description = Column(
        String(255),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
