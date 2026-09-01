from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime
)

from sqlalchemy.sql import func

from app.database import Base


class Baby(Base):

    __tablename__ = "babies"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String(64),
        nullable=False
    )

    parent_user_id_a = Column(
        Integer,
        nullable=False
    )

    parent_user_id_b = Column(
        Integer,
        nullable=False
    )

    gender = Column(
        String(20),
        default="unknown",
        nullable=False
    )

    level = Column(
        Integer,
        default=1,
        nullable=False
    )

    experience = Column(
        Integer,
        default=0,
        nullable=False
    )

    happiness = Column(
        Integer,
        default=100,
        nullable=False
    )

    hunger = Column(
        Integer,
        default=100,
        nullable=False
    )

    health = Column(
        Integer,
        default=100,
        nullable=False
    )

    born_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class BabyRequest(Base):

    __tablename__ = "baby_requests"

    id = Column(
        Integer,
        primary_key=True
    )

    sender_user_id = Column(
        Integer,
        nullable=False
    )

    receiver_user_id = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String(30),
        default="pending",
        nullable=False
    )

    baby_name = Column(
        String(64),
        nullable=True
    )

    baby_gender = Column(
        String(20),
        default="unknown"
    )

    message = Column(
        String(255),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    handled_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
