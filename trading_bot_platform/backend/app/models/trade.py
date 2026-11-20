from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    symbol = Column(String(50), nullable=False)
    side = Column(String(10), nullable=False)  # buy / sell
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=False)
    pnl = Column(Float, default=0.0)
    status = Column(String(20), default="open")  # open / closed / cancelled

    aggressiveness_at_trade = Column(Integer, nullable=True)
    strategy_name = Column(String(100), default="ema_crossover")

    is_paper = Column(Boolean, default=True)
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
