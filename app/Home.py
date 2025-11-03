from data_fetch import get_eth_ohlcv
import streamlit as st
import pandas as pd

st.set_page_config(page_title="ETH/USDT ARIMA", layout="wide")
st.title("ETH/USDT ARIMA – Cloud App")
st.caption(
    "Live data via Binance (auto-fallback to CoinGecko when blocked). "
    "Choose interval & history, then explore the chart."
)

# ---- Controls
cols = st.columns(3)
with cols[0]:
    interval = st.selectbox(
        "Candle interval",
        ["1h", "4h", "1d"],
        index=0,
        help="Exchange kline intervals"
    )
with cols[1]:
    lookback = st.slider(
        "Number of candles",
        min_value=100, max_value=1000, value=500, step=50,
        help="How many most-recent candles to fetch"
    )
with cols[2]:
    refresh = st.button("↻ Refresh data", help="Bypass cache and refetch")

# ---- Cached fetcher
@st.cache_data(ttl=300, show_spinner=False)
def _fetch(interval: str, limit: int) -> pd.DataFrame:
    return get_eth_ohlcv(interval=interval, limit=limit)

# ---- Load data
try:
    if refresh:
        st.cache_data.clear()
    df = _fetch(interval, lookback)
    if df.empty:
        st.warning("No data returned from the data source.")
        st.stop()
except Exception as e:
    st.error(f"Failed to fetch data: {e}")
    st.stop()

# ---- Basic info
st.subheader("Latest snapshot")
last_row = df.iloc[-1]
st.write(
    f"**Last close:** ${last_row['close']:.2f}  | "
    f"**Candle time (open):** {last_row['open_time'].strftime('%Y-%m-%d %H:%M')}"
)

# ---- Chart
st.subheader("ETH/USDT Close Price")
st.line_chart(df.set_index("open_time")["close"], height=360)

with st.expander("Show raw OHLC data"):
    st.dataframe(df.tail(50), use_container_width=True)

# ---- Analysis Sections
from stationarity import run_stationarity_app
from modeling import run_arima_app

st.markdown("---")
run_stationarity_app(df)

st.markdown("---")
run_arima_app(df)
