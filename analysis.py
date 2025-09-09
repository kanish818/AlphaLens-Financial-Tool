import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

def get_clean_factor_and_forward_returns(factor, prices, periods=(1, 5, 10)):
    """
    Formats the factor data, calculates forward returns for multiple periods,
    and adds factor quantiles.
    """
    # Use 'adj close' if available, otherwise fall back to 'close' for robustness.
    price_col = 'adj close' if 'adj close' in prices.columns else 'close'
    if price_col not in prices.columns:
        st.error("The downloaded data is missing a usable price column ('adj close' or 'close').")
        return None

    factor_data = pd.DataFrame(factor)
    factor_data.columns = ['factor']
    
    # Calculate forward returns
    for period in periods:
        factor_data[f'{period}D'] = prices[price_col].pct_change(period).shift(-period)
    
    # Add factor quantiles
    try:
        factor_data['factor_quantile'] = pd.qcut(factor_data['factor'], 5, labels=False) + 1
    except ValueError:
        st.warning("Could not compute 5 quantiles. The factor may have low variance.")
        factor_data['factor_quantile'] = 1
        
    return factor_data.dropna()

def create_returns_analysis(factor_data, periods=(1, 5, 10)):
    """Generates plots and summary tables for returns analysis."""
    st.write("##### Mean Return by Factor Quantile")
    st.write("Shows the average forward return for each portfolio group (quantile). A monotonic trend is desirable.")
    mean_return_by_q = factor_data.groupby('factor_quantile')[[f'{p}D' for p in periods]].mean() * 10000 # In BPS

    fig, ax = plt.subplots(figsize=(12, 6))
    mean_return_by_q.plot(kind='bar', ax=ax)
    ax.set(xlabel='Factor Quantile', ylabel='Mean Forward Return (bps)')
    st.pyplot(fig)

    st.write("##### Cumulative Return by Quantile (1-Day Forward Returns)")
    st.write("Shows the cumulative performance of each quantile portfolio over time.")
    returns_by_q = factor_data.groupby('factor_quantile')['1D'].apply(lambda x: (1 + x).cumprod())
    
    fig, ax = plt.subplots(figsize=(12, 6))
    returns_by_q.unstack(level=0).plot(ax=ax, colormap='viridis')
    ax.set(xlabel='Date', ylabel='Cumulative Returns')
    st.pyplot(fig)

    # Returns Analysis Table
    summary = {}
    for period in periods:
        period_col = f'{period}D'
        top_q = factor_data[factor_data['factor_quantile'] == 5][period_col].mean() * 10000
        bottom_q = factor_data[factor_data['factor_quantile'] == 1][period_col].mean() * 10000
        spread = top_q - bottom_q
        summary[period] = {'Mean Top Quantile (bps)': top_q,
                           'Mean Bottom Quantile (bps)': bottom_q,
                           'Spread (bps)': spread}
    st.write("###### Returns Summary")
    st.dataframe(pd.DataFrame(summary).round(2))

def create_information_analysis(factor_data, periods=(1, 5, 10)):
    """Generates plots and summary tables for information analysis (IC)."""
    ic_data = pd.DataFrame()
    for period in periods:
        # Calculate Spearman rank correlation (Information Coefficient)
        ic = factor_data[['factor', f'{period}D']].groupby(level=0).apply(lambda x: spearmanr(x['factor'], x[f'{period}D'])[0])
        ic_data[f'{period}D_IC'] = ic

    st.write("##### Information Coefficient (IC) Over Time")
    st.write("IC measures the correlation between the factor and future returns. A stable, positive IC is desirable.")
    fig, ax = plt.subplots(figsize=(12, 6))
    ic_data.plot(ax=ax, alpha=0.7)
    for col in ic_data.columns:
        ic_data[col].rolling(22).mean().plot(ax=ax, label=f'{col} (1M MA)')
    ax.set(xlabel='Date', ylabel='Information Coefficient')
    ax.legend()
    st.pyplot(fig)
    
    # Information Analysis Table
    summary = {}
    for col in ic_data.columns:
        ic_series = ic_data[col].dropna()
        t_stat = ic_series.mean() / (ic_series.std() / np.sqrt(len(ic_series)))
        p_value = 0 # Simplified p-value for demonstration
        summary[col.replace('_IC', '')] = {
            'IC Mean': ic_series.mean(),
            'IC Std.': ic_series.std(),
            't-stat(IC)': t_stat,
            'p-value(IC)': p_value
        }
    st.write("###### Information Summary")
    st.dataframe(pd.DataFrame(summary).round(4))

def create_turnover_analysis(factor_data):
    """Analyzes how frequently the factor changes quantiles."""
    st.write("##### Factor Rank Autocorrelation")
    st.write("Measures how quickly the factor ranking decays. Higher values indicate lower turnover (less trading).")
    
    factor_rank = factor_data['factor'].rank()
    autocorrelation = [factor_rank.autocorr(lag=lag) for lag in [1, 5, 10]]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    pd.Series(autocorrelation, index=[1, 5, 10]).plot(kind='bar', ax=ax)
    ax.set(xlabel='Lag (Days)', ylabel='Rank Autocorrelation', title='Factor Rank Autocorrelation')
    st.pyplot(fig)

