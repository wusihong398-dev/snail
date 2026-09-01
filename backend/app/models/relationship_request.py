from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime
)

from sqlalchemy.sql import func

from app.database import Base


class RelationshipRequest(Base):

    __tablename__ = "relationship_requests"

    id = Column(
        Integer,
        primary_key=True
    )

    request_type = Column(
        String(30),
        nullable=False
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
