from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint
)

from sqlalchemy.sql import func

from app.database import Base


class UserRelationship(Base):

    __tablename__ = "user_relationships"

    __table_args__ = (
        UniqueConstraint(
            "user_id_a",
            "user_id_b",
            name="user_relationships_pair_unique"
        ),
    )

    id = Column(
        Integer,
        primary_key=True
    )

    user_id_a = Column(
        Integer,
        nullable=False
    )

    user_id_b = Column(
        Integer,
        nullable=False
    )

    intimacy = Column(
        Integer,
        default=0,
        nullable=False
    )

    # normal / love / married
    relationship_status = Column(
        String(30),
        default="normal",
        nullable=False
    )

    love_started_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    married_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
