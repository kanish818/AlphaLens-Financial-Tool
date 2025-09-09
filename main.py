import streamlit as st
import datetime
import seaborn as sns

# Import functions from other modules
from data_loader import get_stock_data
from factor_creation import generate_mock_news, analyze_sentiment, create_sentiment_factor
from analysis import get_clean_factor_and_forward_returns, create_returns_analysis, create_information_analysis, create_turnover_analysis

# --- Page Configuration ---
st.set_page_config(
    page_title="AlphaLens - AI Financial Analysis",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Use seaborn for better plot aesthetics
sns.set_style("whitegrid")

# --- UI Layout ---
st.title("AlphaLens: AI-Powered Financial Analysis Tool")
st.markdown("""
This dashboard demonstrates an AI-driven analysis tool that leverages simulated NLP to process unstructured data (like news) 
and assess its impact on stock performance.
""")

# --- Sidebar Inputs ---
st.sidebar.header("Analysis Configuration")
TICKER = st.sidebar.text_input("Enter Stock Ticker:", "AAPL").upper()
end_date = datetime.date.today()
# Increased default range for more meaningful statistical analysis
start_date = st.sidebar.date_input("Start Date", end_date - datetime.timedelta(days=365*5)) 

if st.sidebar.button("Run Analysis", type="primary"):
    with st.spinner(f"Fetching data and generating insights for {TICKER}..."):
        pricing = get_stock_data(TICKER, start_date, end_date)
        if pricing.empty:
            st.warning("Could not retrieve stock data. Please check the ticker or date range.")
        else:
            mock_news = generate_mock_news(TICKER, pricing.index)
            sentiment_df = analyze_sentiment(mock_news)
            sentiment_factor = create_sentiment_factor(pricing, sentiment_df)
            st.success("Data processing complete!")

    if not pricing.empty and sentiment_factor is not None:
        st.header("Interactive Factor Analysis Tear Sheet")
        
        # Prepare data for all analysis modules
        factor_data = get_clean_factor_and_forward_returns(sentiment_factor, pricing)

        if factor_data is None or factor_data.empty:
            st.error("Could not generate factor data for analysis. The date range may be too short or the factor may have no variance.")
        else:
            # Create tabs for different analyses for a clean layout
            returns_tab, ic_tab, turnover_tab = st.tabs(["Returns Analysis", "Information Analysis", "Turnover Analysis"])
            
            with returns_tab:
                create_returns_analysis(factor_data)
            
            with ic_tab:
                create_information_analysis(factor_data)

            with turnover_tab:
                create_turnover_analysis(factor_data)
else:
    st.info("Enter a stock ticker and click 'Run Analysis' to begin.")

