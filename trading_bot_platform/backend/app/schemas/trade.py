from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TradeOut(BaseModel):
    id: int
    symbol: str
    side: str
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    pnl: float
    status: str
    aggressiveness_at_trade: Optional[int]
    strategy_name: str
    is_paper: bool
    opened_at: datetime
    closed_at: Optional[datetime]

    class Config:
        from_attributes = True


class BotStatus(BaseModel):
    is_running: bool
    aggressiveness: int
    paper_trading: bool
    current_balance: float
    total_pnl: float
    open_positions: int
    last_signal: Optional[str] = None
    message: str = ""
