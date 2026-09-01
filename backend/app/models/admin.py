from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)

from sqlalchemy.sql import func

from app.database import Base


class Admin(Base):

    __tablename__ = "admins"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    # 登录账号
    username = Column(
        String(64),
        unique=True,
        index=True,
        nullable=False
    )


    # 加密密码
    password_hash = Column(
        String(255),
        nullable=False
    )


    # 权限角色
    # admin / operator
    role = Column(
        String(32),
        default="admin"
    )


    # 是否启用
    enabled = Column(
        Boolean,
        default=True
    )


    # 创建时间
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
