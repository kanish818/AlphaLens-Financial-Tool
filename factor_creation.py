import pandas as pd
import random

def generate_mock_news(ticker, dates):
    """
    Generates a DataFrame of mock news headlines for a given ticker and date range.
    This simulates fetching unstructured data from news APIs.
    """
    positive_keywords = ["surges", "upgrades", "beats expectations", "record profits", "innovates", "expands", "optimistic", "strong growth"]
    negative_keywords = ["plummets", "downgrades", "misses estimates", "reports loss", "investigation", "declines", "pessimistic", "headwinds"]
    sources = ["Reuters", "Bloomberg", "Financial Times", "Wall Street Journal", "TechCrunch"]
    
    news_data = []
    for date in dates:
        # 70% chance of news on any given day
        if random.random() > 0.3:
            # 60% positive bias for the news
            keyword = random.choice(positive_keywords if random.random() > 0.4 else negative_keywords)
            headline = f"{ticker} {keyword} on new product announcement."
            news_data.append([date, headline, random.choice(sources)])
            
    return pd.DataFrame(news_data, columns=['date', 'headline', 'source']).set_index('date')

def analyze_sentiment(news_df):
    """
    Simulates a sentiment analysis module using NLP by scoring headlines based on keywords.
    """
    if news_df.empty:
        return news_df
        
    positive_keywords = ["surges", "upgrades", "beats", "profits", "innovates", "expands", "optimistic", "strong growth"]
    
    def get_score(headline):
        # Simple scoring: +1 if a positive keyword is present, -1 otherwise.
        return 1 if any(word in headline for word in positive_keywords) else -1
        
    news_df['sentiment_score'] = news_df['headline'].apply(get_score)
    return news_df

def create_sentiment_factor(prices, sentiment_data):
    """
    Creates a smoothed alpha factor from the sentiment scores.
    """
    if sentiment_data.empty:
        return None
        
    # Align sentiment data with pricing data, forward-filling missing days
    daily_sentiment = sentiment_data['sentiment_score'].reindex(prices.index, method='ffill').fillna(0)
    
    # Smooth the factor using a 5-day rolling average to reduce noise
    sentiment_factor = daily_sentiment.rolling(window=5, min_periods=1).mean()
    
    return sentiment_factor

