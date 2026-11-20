from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdateSettings(BaseModel):
    aggressiveness: Optional[int] = Field(None, ge=1, le=10)
    paper_trading: Optional[bool] = None
    exchange_name: Optional[str] = None
    exchange_api_key: Optional[str] = None
    exchange_api_secret: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    aggressiveness: int
    is_bot_running: bool
    paper_trading: bool
    current_balance: float
    total_pnl: float
    open_positions: int
    exchange_name: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
