from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class UserEntitlement(Base):
    __tablename__ = "user_entitlements"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    entitlement_key = Column(String(100), nullable=False)
    quantity = Column(Integer, default=0, nullable=False)
    scope_type = Column(String(30), default="global", nullable=False)
    scope_id = Column(Integer, nullable=True)
    source_type = Column(String(30), default="purchase", nullable=False)
    source_id = Column(Integer, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
