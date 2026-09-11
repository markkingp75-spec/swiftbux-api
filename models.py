from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    balance = Column(Numeric(10, 2), default=0.00)
    currency = Column(String, default="KWD")
    referral_code = Column(String, unique=True, index=True)
    referred_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    amount = Column(Numeric(10, 2))
    type = Column(String)  # 'task_reward' or 'payout'
    method = Column(String, nullable=True)
    destination = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)