"""
Simpel EMA Crossover strategi.
Kan nemt udskiftes med din egen strategi.
"""

from typing import Optional, Dict, Any
import pandas as pd


def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def generate_signal(df: pd.DataFrame, fast: int = 9, slow: int = 21) -> Optional[str]:
    """
    Returnerer 'buy', 'sell' eller None.
    Forventer df med kolonner: open, high, low, close, volume
    """
    if len(df) < slow + 5:
        return None

    df = df.copy()
    df["ema_fast"] = calculate_ema(df["close"], fast)
    df["ema_slow"] = calculate_ema(df["close"], slow)

    # Sidste to candles
    prev_fast = df["ema_fast"].iloc[-2]
    prev_slow = df["ema_slow"].iloc[-2]
    curr_fast = df["ema_fast"].iloc[-1]
    curr_slow = df["ema_slow"].iloc[-1]

    # Bullish crossover
    if prev_fast <= prev_slow and curr_fast > curr_slow:
        return "buy"

    # Bearish crossover
    if prev_fast >= prev_slow and curr_fast < curr_slow:
        return "sell"

    return None


def get_position_size(
    balance: float,
    aggressiveness: int,
    price: float,
    risk_per_trade: float = 0.01,
) -> float:
    """
    Beregner position size baseret på aggressivitet (1-10).
    aggressiveness 1 = meget forsigtig, 10 = aggressiv.
    """
    # Base risk 0.5% → 5% afhængig af aggressivitet
    risk_pct = 0.005 + (aggressiveness - 1) * 0.005  # 0.5% til 5%
    risk_amount = balance * risk_pct

    # Simpel fixed fractional – kan udvides med ATR osv.
    quantity = risk_amount / price
    return round(quantity, 6)


def get_stop_loss_take_profit(
    entry_price: float,
    side: str,
    aggressiveness: int,
) -> Dict[str, float]:
    """
    Returnerer stop-loss og take-profit priser.
    Lavere aggressivitet = tættere stops.
    """
    # Base SL 1%, TP 2% → mere aggressiv = bredere SL men højere TP
    sl_pct = 0.008 + (aggressiveness - 1) * 0.002   # 0.8% → 2.6%
    tp_pct = 0.015 + (aggressiveness - 1) * 0.004   # 1.5% → 5.1%

    if side == "buy":
        stop_loss = entry_price * (1 - sl_pct)
        take_profit = entry_price * (1 + tp_pct)
    else:
        stop_loss = entry_price * (1 + sl_pct)
        take_profit = entry_price * (1 - tp_pct)

    return {
        "stop_loss": round(stop_loss, 2),
        "take_profit": round(take_profit, 2),
        "sl_pct": round(sl_pct * 100, 2),
        "tp_pct": round(tp_pct * 100, 2),
    }
