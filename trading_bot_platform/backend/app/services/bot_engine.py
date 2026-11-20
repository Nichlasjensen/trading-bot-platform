"""
Paper-trading bot engine.
Kører i baggrunden for hver bruger der har botten tændt.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, Optional
import pandas as pd
import ccxt.async_support as ccxt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.user import User
from app.models.trade import Trade
from app.strategies.ema_crossover import (
    generate_signal,
    get_position_size,
    get_stop_loss_take_profit,
)
from app.core.config import get_settings

settings = get_settings()

# Global state for running bots
_running_bots: Dict[int, asyncio.Task] = {}
_last_signals: Dict[int, str] = {}


async def fetch_ohlcv(symbol: str = "BTC/USDT", timeframe: str = "15m", limit: int = 100) -> pd.DataFrame:
    """Henter OHLCV data via CCXT (public, ingen API-nøgle nødvendig)."""
    exchange = ccxt.binance({"enableRateLimit": True})
    try:
        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    finally:
        await exchange.close()


async def run_bot_for_user(user_id: int, db_session_factory):
    """Hovedloop for én brugers bot."""
    print(f"[BOT] Starter bot for user_id={user_id}")

    while True:
        try:
            async with db_session_factory() as db:
                result = await db.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()

                if not user or not user.is_bot_running:
                    print(f"[BOT] Stopper bot for user_id={user_id}")
                    break

                # Hent markedsdata
                df = await fetch_ohlcv(settings.DEFAULT_SYMBOL, settings.DEFAULT_TIMEFRAME)
                signal = generate_signal(df)

                if signal:
                    _last_signals[user_id] = f"{signal.upper()} @ {df['close'].iloc[-1]:.2f}"

                    # Tjek om der allerede er en åben position
                    open_trades = await db.execute(
                        select(Trade).where(
                            Trade.user_id == user_id,
                            Trade.status == "open"
                        )
                    )
                    open_trade = open_trades.scalar_one_or_none()

                    current_price = float(df["close"].iloc[-1])

                    if signal == "buy" and open_trade is None:
                        # Åbn long
                        qty = get_position_size(user.current_balance, user.aggressiveness, current_price)
                        if qty * current_price > user.current_balance * 0.95:
                            qty = (user.current_balance * 0.9) / current_price

                        levels = get_stop_loss_take_profit(current_price, "buy", user.aggressiveness)

                        trade = Trade(
                            user_id=user_id,
                            symbol=settings.DEFAULT_SYMBOL,
                            side="buy",
                            entry_price=current_price,
                            quantity=qty,
                            status="open",
                            aggressiveness_at_trade=user.aggressiveness,
                            strategy_name="ema_crossover",
                            is_paper=user.paper_trading,
                        )
                        db.add(trade)

                        user.open_positions = 1
                        user.current_balance -= qty * current_price  # reserverer kapital (paper)
                        await db.commit()
                        print(f"[BOT] BUY {qty:.6f} {settings.DEFAULT_SYMBOL} @ {current_price} (user {user_id})")

                    elif signal == "sell" and open_trade is not None and open_trade.side == "buy":
                        # Luk long
                        exit_price = current_price
                        pnl = (exit_price - open_trade.entry_price) * open_trade.quantity

                        open_trade.exit_price = exit_price
                        open_trade.pnl = pnl
                        open_trade.status = "closed"
                        open_trade.closed_at = datetime.now(timezone.utc)

                        user.current_balance += open_trade.quantity * exit_price
                        user.total_pnl += pnl
                        user.open_positions = 0
                        await db.commit()
                        print(f"[BOT] SELL (luk) PnL={pnl:.2f} (user {user_id})")

                # Simpel stop-loss / take-profit check på åbne trades
                open_trades = await db.execute(
                    select(Trade).where(Trade.user_id == user_id, Trade.status == "open")
                )
                for trade in open_trades.scalars().all():
                    levels = get_stop_loss_take_profit(trade.entry_price, trade.side, trade.aggressiveness_at_trade or 5)
                    current_price = float(df["close"].iloc[-1])

                    should_close = False
                    if trade.side == "buy":
                        if current_price <= levels["stop_loss"] or current_price >= levels["take_profit"]:
                            should_close = True
                    else:
                        if current_price >= levels["stop_loss"] or current_price <= levels["take_profit"]:
                            should_close = True

                    if should_close:
                        exit_price = current_price
                        pnl = (exit_price - trade.entry_price) * trade.quantity if trade.side == "buy" else (trade.entry_price - exit_price) * trade.quantity
                        trade.exit_price = exit_price
                        trade.pnl = pnl
                        trade.status = "closed"
                        trade.closed_at = datetime.now(timezone.utc)

                        user.current_balance += trade.quantity * exit_price
                        user.total_pnl += pnl
                        user.open_positions = max(0, user.open_positions - 1)
                        await db.commit()
                        print(f"[BOT] SL/TP lukket PnL={pnl:.2f} (user {user_id})")

        except Exception as e:
            print(f"[BOT] Fejl for user {user_id}: {e}")

        # Vent 60 sekunder mellem checks (kan gøres frekvens-afhængig)
        await asyncio.sleep(60)


def start_bot(user_id: int, db_session_factory):
    if user_id in _running_bots and not _running_bots[user_id].done():
        return False  # allerede kørende

    task = asyncio.create_task(run_bot_for_user(user_id, db_session_factory))
    _running_bots[user_id] = task
    return True


def stop_bot(user_id: int):
    task = _running_bots.get(user_id)
    if task and not task.done():
        task.cancel()
        del _running_bots[user_id]
        return True
    return False


def get_last_signal(user_id: int) -> Optional[str]:
    return _last_signals.get(user_id)
