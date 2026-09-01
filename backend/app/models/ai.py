from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    ForeignKey
)

from app.database import Base



class AIConfig(Base):

    __tablename__="ai_configs"


    id = Column(
        Integer,
        primary_key=True
    )


    name = Column(
        String(100),
        nullable=False
    )


    display_name = Column(
        String(100),
        default="蜗牛小精灵"
    )


    provider = Column(
        String(100),
        nullable=False
    )


    api_url = Column(
        String(255),
        nullable=False
    )


    api_key = Column(
        Text,
        nullable=False
    )


    model = Column(
        String(100),
        nullable=False
    )


    proxy_id = Column(
        Integer,
        ForeignKey(
            "proxy_configs.id"
        ),
        nullable=True
    )


    system_prompt = Column(
        Text,
        default=""
    )


    enabled = Column(
        Boolean,
        default=True
    )


    priority = Column(
        Integer,
        default=1
    )
