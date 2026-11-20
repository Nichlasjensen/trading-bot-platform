from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "Trading Bot Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "skift-denne-til-en-lang-random-string-i-produktion-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 dage

    # Database – på Render kan du sætte DATABASE_URL til Postgres
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./trading_bot.db")

    # Trading defaults
    DEFAULT_SYMBOL: str = "BTC/USDT"
    DEFAULT_TIMEFRAME: str = "15m"
    PAPER_TRADING: bool = True

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
