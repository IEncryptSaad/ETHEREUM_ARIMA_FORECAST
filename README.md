# ETHEREUM ARIMA FORECAST

Cloud-based Ethereum (ETH/USDT) price forecasting app using ARIMA time series modeling.
Built with Streamlit, Python, and Binance public API for historical data.
Fully deployed on Streamlit Community Cloud — zero local storage.

## Features
- Fetch ETH/USDT OHLCV from Binance (public, no key)
- EDA: trends, volatility, rolling stats
- Stationarity testing (ADF) + ACF/PACF
- ARIMA modeling (manual grid + optional auto-ARIMA)
- Residual diagnostics and backtest metrics (RMSE, MAPE)
- 30-day forecast with confidence intervals

## Run (Streamlit Cloud)
Deploy this repo directly on Streamlit Community Cloud.

## Project layout (planned)
- app/
  - Home.py
  - data_fetch.py
  - eda.py
  - stationarity.py
  - modeling.py
  - evaluate.py
- requirements.txt
- .gitignore
- .streamlit/
  - config.toml
