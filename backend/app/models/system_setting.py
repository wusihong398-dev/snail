from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime
)

from sqlalchemy.sql import func

from app.database import Base


class SystemSetting(Base):

    __tablename__ = "system_settings"

    id = Column(
        Integer,
        primary_key=True
    )

    setting_key = Column(
        String(100),
        unique=True,
        nullable=False
    )

    setting_value = Column(
        String(255),
        nullable=False
    )

    value_type = Column(
        String(30),
        default="string",
        nullable=False
    )

    title = Column(
        String(128),
        nullable=False
    )

    description = Column(
        String(255),
        nullable=True
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
