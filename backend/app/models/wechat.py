from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)

from sqlalchemy.sql import func

from app.database import Base


class WechatAccount(Base):

    __tablename__ = "wechat_accounts"


    id = Column(
        Integer,
        primary_key=True
    )


    # 微信昵称
    nickname = Column(
        String(64)
    )


    # 微信账号
    wxid = Column(
        String(128),
        unique=True
    )


    # 登录状态
    online = Column(
        Boolean,
        default=False
    )


    # 所属客户
    customer_id = Column(
        Integer
    )


    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
