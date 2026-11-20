from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, AsyncSessionLocal
from app.api.deps import get_current_user
from app.models.user import User
from app.models.trade import Trade
from app.schemas.user import UserOut, UserUpdateSettings
from app.schemas.trade import TradeOut, BotStatus
from app.services.bot_engine import start_bot, stop_bot, get_last_signal

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me/settings", response_model=UserOut)
async def update_settings(
    settings_in: UserUpdateSettings,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if settings_in.aggressiveness is not None:
        current_user.aggressiveness = settings_in.aggressiveness
    if settings_in.paper_trading is not None:
        current_user.paper_trading = settings_in.paper_trading
    if settings_in.exchange_name is not None:
        current_user.exchange_name = settings_in.exchange_name
    if settings_in.exchange_api_key is not None:
        current_user.exchange_api_key = settings_in.exchange_api_key
    if settings_in.exchange_api_secret is not None:
        current_user.exchange_api_secret = settings_in.exchange_api_secret

    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/me/bot/start", response_model=BotStatus)
async def start_my_bot(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.is_bot_running:
        return BotStatus(
            is_running=True,
            aggressiveness=current_user.aggressiveness,
            paper_trading=current_user.paper_trading,
            current_balance=current_user.current_balance,
            total_pnl=current_user.total_pnl,
            open_positions=current_user.open_positions,
            last_signal=get_last_signal(current_user.id),
            message="Bot kører allerede",
        )

    current_user.is_bot_running = True
    await db.commit()

    started = start_bot(current_user.id, AsyncSessionLocal)
    return BotStatus(
        is_running=True,
        aggressiveness=current_user.aggressiveness,
        paper_trading=current_user.paper_trading,
        current_balance=current_user.current_balance,
        total_pnl=current_user.total_pnl,
        open_positions=current_user.open_positions,
        last_signal=get_last_signal(current_user.id),
        message="Bot startet" if started else "Bot startet (allerede i gang)",
    )


@router.post("/me/bot/stop", response_model=BotStatus)
async def stop_my_bot(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user.is_bot_running = False
    await db.commit()
    stop_bot(current_user.id)

    return BotStatus(
        is_running=False,
        aggressiveness=current_user.aggressiveness,
        paper_trading=current_user.paper_trading,
        current_balance=current_user.current_balance,
        total_pnl=current_user.total_pnl,
        open_positions=current_user.open_positions,
        last_signal=get_last_signal(current_user.id),
        message="Bot stoppet",
    )


@router.get("/me/bot/status", response_model=BotStatus)
async def bot_status(current_user: User = Depends(get_current_user)):
    return BotStatus(
        is_running=current_user.is_bot_running,
        aggressiveness=current_user.aggressiveness,
        paper_trading=current_user.paper_trading,
        current_balance=current_user.current_balance,
        total_pnl=current_user.total_pnl,
        open_positions=current_user.open_positions,
        last_signal=get_last_signal(current_user.id),
        message="OK",
    )


@router.get("/me/trades", response_model=list[TradeOut])
async def my_trades(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
):
    result = await db.execute(
        select(Trade)
        .where(Trade.user_id == current_user.id)
        .order_by(Trade.opened_at.desc())
        .limit(limit)
    )
    return result.scalars().all()
