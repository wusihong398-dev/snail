from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)

from sqlalchemy.sql import func

from app.database import Base


class User(Base):

    __tablename__ = "users"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    # 微信用户ID
    wx_user_id = Column(
        String(128),
        unique=True,
        index=True,
        nullable=False
    )


    # 微信昵称
    nickname = Column(
        String(64),
        default=""
    )


    # 头像
    avatar = Column(
        String(255),
        default=""
    )


    # 等级
    level = Column(
        Integer,
        default=1
    )


    # 蜗币
    coins = Column(
        Integer,
        default=0
    )


    # 经验值
    experience = Column(
        Integer,
        default=0
    )


    # 真实付费获得的钻石
    paid_diamonds = Column(
        Integer,
        default=0,
        nullable=False
    )


    # 会员/活动/管理员赠送的奖励钻石
    bonus_diamonds = Column(
        Integer,
        default=0,
        nullable=False
    )


    # 是否启用
    is_active = Column(
        Boolean,
        default=True
    )


    # 会员等级
    # normal / vip / svip
    member_level = Column(
        String(30),
        default="normal"
    )


    # 会员开始时间
    member_started_at = Column(
        DateTime(timezone=True),
        nullable=True
    )


    # 会员到期时间
    member_expire_at = Column(
        DateTime(timezone=True),
        nullable=True
    )


    # 创建时间
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
