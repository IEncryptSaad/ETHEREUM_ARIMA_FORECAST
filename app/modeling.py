import streamlit as st
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import numpy as np
import matplotlib.pyplot as plt


def fit_arima(series, order=(1, 1, 1)):
    """Fit an ARIMA model to the given series."""
    model = ARIMA(series, order=order)
    model_fit = model.fit()
    return model_fit


def forecast_arima(model_fit, steps=30):
    """Generate forecasts from a fitted ARIMA model."""
    forecast = model_fit.forecast(steps=steps)
    return forecast


def run_arima_app(df: pd.DataFrame):
    st.header("📈 ARIMA Modeling and Forecasts")

    close_series = df["close"].dropna()
    st.subheader("Select Model Parameters (p, d, q)")
    p = st.number_input("p (Auto-Regressive order)", 0, 10, 1)
    d = st.number_input("d (Differencing order)", 0, 2, 1)
    q = st.number_input("q (Moving-Average order)", 0, 10, 1)
    steps = st.slider("Forecast Days Ahead", 5, 60, 30)
    run = st.button("Train and Forecast")

    if run:
        with st.spinner("Training ARIMA model..."):
            model_fit = fit_arima(close_series, order=(p, d, q))
            forecast = forecast_arima(model_fit, steps)

        st.success("✅ Model trained successfully!")

        # Evaluation on last 10% as holdout
        train_size = int(len(close_series) * 0.9)
        train, test = close_series[:train_size], close_series[train_size:]
        model = ARIMA(train, order=(p, d, q)).fit()
        preds = model.forecast(steps=len(test))
        rmse = np.sqrt(mean_squared_error(test, preds))
        mape = mean_absolute_percentage_error(test, preds) * 100

        st.metric("RMSE", f"{rmse:.2f}")
        st.metric("MAPE (%)", f"{mape:.2f}")

        # Plot forecast
        st.subheader("Forecast Plot")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(close_series.index, close_series, label="Actual")
        future_index = pd.date_range(
            close_series.index[-1], periods=steps + 1, freq="D"
        )[1:]
        ax.plot(future_index, forecast, label="Forecast", color="orange")
        ax.legend()
        st.pyplot(fig)

        # ---- Preview + Download Forecast as CSV
        fc_df = pd.DataFrame({"date": future_index, "forecast": forecast})
        st.subheader("Forecast Data (first few rows)")
        st.dataframe(fc_df.head(), use_container_width=True)
        st.download_button(
            "⬇️ Download forecast as CSV",
            fc_df.to_csv(index=False).encode("utf-8"),
            file_name="eth_arima_forecast.csv",
            mime="text/csv",
        )
