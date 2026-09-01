from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class DiamondTransaction(Base):
    __tablename__ = "diamond_transactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    transaction_type = Column(String(50), nullable=False)
    diamond_type = Column(String(20), nullable=False)
    amount = Column(Integer, nullable=False)
    paid_before = Column(Integer, default=0, nullable=False)
    paid_after = Column(Integer, default=0, nullable=False)
    bonus_before = Column(Integer, default=0, nullable=False)
    bonus_after = Column(Integer, default=0, nullable=False)
    order_id = Column(Integer, nullable=True)
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(Integer, nullable=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
