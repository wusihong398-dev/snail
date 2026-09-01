from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime
)

from sqlalchemy.sql import func

from app.database import Base


class ShopProduct(Base):

    __tablename__ = "shop_products"


    id = Column(
        Integer,
        primary_key=True
    )


    # 商品名称
    name = Column(
        String(128),
        nullable=False
    )


    # member / gift / pet / decoration
    product_type = Column(
        String(30),
        default="member",
        nullable=False
    )


    # vip / svip
    member_level = Column(
        String(30),
        nullable=True
    )


    # 会员有效天数
    member_days = Column(
        Integer,
        nullable=True
    )


    # 人民币价格，单位：分
    price_cents = Column(
        Integer,
        default=0
    )


    # 蜗币价格
    coin_price = Column(
        Integer,
        default=0
    )


    # 是否上架
    enabled = Column(
        Boolean,
        default=True
    )


    # 排序
    sort_order = Column(
        Integer,
        default=0
    )


    description = Column(
        Text,
        nullable=True
    )


    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
