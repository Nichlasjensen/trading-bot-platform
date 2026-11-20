from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)

    # Trading settings
    aggressiveness = Column(Integer, default=5)  # 1-10
    is_bot_running = Column(Boolean, default=False)
    paper_trading = Column(Boolean, default=True)

    # Optional exchange keys (encrypted in production!)
    exchange_api_key = Column(Text, nullable=True)
    exchange_api_secret = Column(Text, nullable=True)
    exchange_name = Column(String(50), default="binance")

    # Bot state
    current_balance = Column(Float, default=10000.0)  # Paper start balance
    total_pnl = Column(Float, default=0.0)
    open_positions = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
