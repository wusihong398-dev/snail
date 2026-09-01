from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime
)

from sqlalchemy.sql import func

from app.database import Base


class GiftProduct(Base):

    __tablename__ = "gift_products"

    id = Column(
        Integer,
        primary_key=True
    )

    product_id = Column(
        Integer,
        unique=True,
        nullable=False
    )

    icon_url = Column(
        String(255),
        nullable=True
    )

    rarity = Column(
        String(30),
        default="normal",
        nullable=False
    )

    exp_reward = Column(
        Integer,
        default=0,
        nullable=False
    )

    intimacy_reward = Column(
        Integer,
        default=0,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class GiftRecord(Base):

    __tablename__ = "gift_records"

    id = Column(
        Integer,
        primary_key=True
    )

    order_id = Column(
        Integer,
        unique=True,
        nullable=False
    )

    sender_user_id = Column(
        Integer,
        nullable=False
    )

    receiver_user_id = Column(
        Integer,
        nullable=False
    )

    product_id = Column(
        Integer,
        nullable=False
    )

    gift_name = Column(
        String(128),
        nullable=False
    )

    quantity = Column(
        Integer,
        default=1,
        nullable=False
    )

    coin_amount = Column(
        Integer,
        default=0,
        nullable=False
    )

    exp_reward = Column(
        Integer,
        default=0,
        nullable=False
    )

    intimacy_reward = Column(
        Integer,
        default=0,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
