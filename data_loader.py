import pandas as pd
import yfinance as yf
import streamlit as st

@st.cache_data
def get_stock_data(ticker, start_date, end_date):
    """
    Fetches historical stock price data from Yahoo Finance.
    - Flattens multi-index columns.
    - Standardizes all column names to lowercase.
    """
    try:
        stock_df = yf.download(ticker, start=start_date, end=end_date)
        if stock_df.empty:
            return pd.DataFrame()
            
        # Handle potential multi-index columns returned by yfinance
        if isinstance(stock_df.columns, pd.MultiIndex):
            stock_df.columns = stock_df.columns.get_level_values(0)
            
        # Standardize all column names to lowercase to prevent KeyErrors
        stock_df.columns = [col.lower() for col in stock_df.columns]
        
        return stock_df
    except Exception as e:
        st.error(f"Error fetching stock data for {ticker}: {e}")
        return pd.DataFrame()

