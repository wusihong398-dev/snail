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



class ProxyConfig(Base):

    __tablename__="proxy_configs"


    id=Column(
        Integer,
        primary_key=True
    )


    name=Column(
        String(100)
    )


    protocol=Column(
        String(30)
    )


    url=Column(
        Text
    )


    server=Column(
        String(255)
    )


    port=Column(
        Integer
    )


    enabled=Column(
        Boolean,
        default=False
    )


    status=Column(
        String(50),
        default="未测试"
    )


    created_at=Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
