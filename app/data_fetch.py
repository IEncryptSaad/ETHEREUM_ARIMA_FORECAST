import math
import pandas as pd
import requests

BINANCE_URL = "https://api.binance.com/api/v3/klines"
COINGECKO_OHLC_URL = "https://api.coingecko.com/api/v3/coins/ethereum/ohlc"

class DataFetchError(Exception):
    pass

def _binance_ohlcv(symbol="ETHUSDT", interval="1h", limit=500) -> pd.DataFrame:
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    r = requests.get(BINANCE_URL, params=params, timeout=12)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(
        data,
        columns=[
            "open_time","open","high","low","close","volume",
            "close_time","quote_asset_volume","num_trades",
            "taker_buy_base","taker_buy_quote","ignore",
        ],
    )
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    for c in ["open","high","low","close","volume"]:
        df[c] = df[c].astype(float)
    return df[["open_time","open","high","low","close","volume"]]

def _round_days_allowed(days_required: int) -> int:
    # CoinGecko only accepts: 1, 7, 14, 30, 90, 180, 365, "max"
    allowed = [1, 7, 14, 30, 90, 180, 365]
    for d in allowed:
        if days_required <= d:
            return d
    return 365

def _coingecko_ohlc(interval: str, candles: int) -> pd.DataFrame:
    # Map requested candles/interval to an approximate number of days
    if interval == "1h":
        days_needed = math.ceil(candles / 24)
    elif interval == "4h":
        days_needed = math.ceil(candles / 6)
    else:  # "1d"
        days_needed = max(1, candles)

    days = _round_days_allowed(days_needed)
    params = {"vs_currency": "usd", "days": days}
    r = requests.get(COINGECKO_OHLC_URL, params=params, timeout=12)
    r.raise_for_status()
    # Response rows: [timestamp(ms), open, high, low, close]
    rows = r.json()
    if not rows:
        raise DataFetchError("CoinGecko returned no data")
    df = pd.DataFrame(rows, columns=["ts","open","high","low","close"])
    df["open_time"] = pd.to_datetime(df["ts"], unit="ms")
    for c in ["open","high","low","close"]:
        df[c] = df[c].astype(float)
    # CoinGecko doesn't include volume in this endpoint
    df["volume"] = pd.NA
    return df[["open_time","open","high","low","close","volume"]]

def get_eth_ohlcv(interval="1h", limit=500) -> pd.DataFrame:
    """
    Try Binance first. If blocked (HTTP 451/403) or any error occurs,
    fall back to CoinGecko OHLC. Returns a DataFrame with columns:
    open_time, open, high, low, close, volume (volume may be NA for fallback).
    """
    try:
        return _binance_ohlcv(symbol="ETHUSDT", interval=interval, limit=limit)
    except requests.HTTPError as e:
        status = e.response.status_code
        if status in (451, 403):
            # Legal block / forbidden → use CoinGecko
            return _coingecko_ohlc(interval, limit)
        # Other HTTP error → still try CoinGecko as a graceful fallback
        return _coingecko_ohlc(interval, limit)
    except Exception:
        # Network/parse errors → fallback
        return _coingecko_ohlc(interval, limit)

