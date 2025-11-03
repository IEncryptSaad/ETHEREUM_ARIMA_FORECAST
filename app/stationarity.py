import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, acf, pacf

# Perform ADF stationarity test
def adf_test(series: pd.Series):
    result = adfuller(series.dropna())
    labels = [
        "ADF Statistic", "p-value", "# Lags Used", "# Observations Used"
    ]
    output = pd.Series(result[0:4], index=labels)
    return output, result[1] <= 0.05  # stationary if p <= 0.05

# Plot ACF and PACF
def plot_acf_pacf(series: pd.Series, lags=40):
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    pd.plotting.autocorrelation_plot(series, ax=ax[0])
    ax[0].set_title("Autocorrelation (ACF)")
    pacf_vals = pacf(series.dropna(), nlags=lags)
    ax[1].stem(range(len(pacf_vals)), pacf_vals, use_line_collection=True)
    ax[1].set_title("Partial Autocorrelation (PACF)")
    plt.tight_layout()
    return fig

# Streamlit section
def run_stationarity_app(df: pd.DataFrame):
    st.header("📉 Stationarity Analysis (ADF + ACF/PACF)")
    target = "close"
    st.write("Using column:", target)

    series = df[target]

    # Run ADF test
    output, stationary = adf_test(series)
    st.subheader("ADF Test Results")
    st.dataframe(output)
    if stationary:
        st.success("✅ Series appears stationary (p ≤ 0.05).")
    else:
        st.warning("⚠️ Series is likely non-stationary (p > 0.05). Differencing may be required.")

    # Plot ACF/PACF
    st.subheader("ACF and PACF Plots")
    st.pyplot(plot_acf_pacf(series))
