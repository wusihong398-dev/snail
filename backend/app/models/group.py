from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text
)

from app.database import Base


class Group(Base):

    __tablename__ = "groups"


    id = Column(
        Integer,
        primary_key=True
    )


    wx_group_id = Column(
        String(128),
        unique=True,
        nullable=True
    )


    group_name = Column(
        String(128),
        nullable=True
    )


    robot_id = Column(
        Integer,
        nullable=True
    )


    # 数据所属购买客户（租户）
    customer_id = Column(
        Integer,
        nullable=True
    )


    enable_ai = Column(
        Boolean,
        default=True
    )


    enable_game = Column(
        Boolean,
        default=True
    )


    enable_social = Column(
        Boolean,
        default=False
    )


    enable_love = Column(
        Boolean,
        default=False
    )


    enable_marriage = Column(
        Boolean,
        default=False
    )


    enable_baby = Column(
        Boolean,
        default=False
    )


    welcome_enabled = Column(
        Boolean,
        default=False
    )


    welcome_text = Column(
        Text,
        nullable=True
    )


    system_prompt = Column(
        Text,
        nullable=True
    )
