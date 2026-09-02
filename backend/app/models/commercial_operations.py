from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class AgentDiamondQuotaTransaction(Base):
    __tablename__ = "agent_diamond_quota_transactions"
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, nullable=False)
    transaction_type = Column(String(40), nullable=False)
    amount = Column(BigInteger, nullable=False)
    quota_before = Column(BigInteger, nullable=False)
    quota_after = Column(BigInteger, nullable=False)
    redeem_code_id = Column(Integer, nullable=True)
    customer_id = Column(Integer, nullable=True)
    operator_type = Column(String(30), nullable=False)
    operator_name = Column(String(128), nullable=False)
    reason = Column(String(255), nullable=False)
    idempotency_key = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AgentLicenseTransaction(Base):
    __tablename__ = "agent_license_transactions"
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, nullable=False)
    transaction_type = Column(String(40), nullable=False)
    amount = Column(Integer, nullable=False)
    balance_before = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    reference_type = Column(String(40), nullable=True)
    reference_id = Column(Integer, nullable=True)
    description = Column(String(255), nullable=True)
    operator_type = Column(String(30), nullable=True)
    operator_name = Column(String(128), nullable=True)
    idempotency_key = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CommercialOperationLog(Base):
    __tablename__ = "commercial_operation_logs"
    id = Column(Integer, primary_key=True)
    operation_type = Column(String(50), nullable=False)
    operator_name = Column(String(128), nullable=False)
    target_type = Column(String(40), nullable=False)
    target_id = Column(Integer, nullable=False)
    details_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
