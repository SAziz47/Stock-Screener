
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import streamlit as st

def get_nifty_tickers():
    return [
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
        'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS',
        'LT.NS', 'AXISBANK.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'WIPRO.NS',
        'BAJFINANCE.NS', 'TITAN.NS', 'ULTRACEMCO.NS', 'SUNPHARMA.NS', 'TATAMOTORS.NS',
        'NTPC.NS', 'POWERGRID.NS', 'M&M.NS', 'HCLTECH.NS', 'ADANIENT.NS',
        'BAJAJFINSV.NS', 'ONGC.NS', 'COALINDIA.NS', 'TATASTEEL.NS', 'HINDALCO.NS',
    ]

def get_stocks_below_ma(tickers, ma_period=200):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=ma_period + 100)
    results_list = []
    
    progress_bar = st.progress(0)
    total_tickers = len(tickers)
    
    for idx, ticker in enumerate(tickers):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)
            
            if len(hist) > ma_period:
                ma_200 = hist['Close'].rolling(window=ma_period).mean()
                current_price = float(hist['Close'].iloc[-1])
                current_ma = float(ma_200.iloc[-1])
                below_ma = current_price < current_ma
                distance_from_ma = ((current_price - current_ma) / current_ma) * 100
                
                volume = hist['Volume'].iloc[-1]
                price_change = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                
                results_list.append({
                    'Symbol': ticker.replace('.NS', ''),
                    'Name': stock.info.get('longName', ticker.replace('.NS', '')),
                    'Current_Price': round(current_price, 2),
                    'MA_200': round(current_ma, 2),
                    'Below_MA': below_ma,
                    'Distance_From_MA_%': round(distance_from_ma, 2),
                    'Volume': volume,
                    'Price_Change_%': round(price_change, 2)
                })
        except Exception as e:
            st.write(f"Error processing {ticker}: {str(e)}")
        
        progress_bar.progress((idx + 1) / total_tickers)
    
    progress_bar.empty()
    return pd.DataFrame(results_list)

def create_charts(analysis_df, stocks_per_chart=15):
    plt.style.use('classic')
    above_df = analysis_df[analysis_df['Distance_From_MA_%'] >= 0].sort_values('Distance_From_MA_%', ascending=True)
    below_df = analysis_df[analysis_df['Distance_From_MA_%'] < 0].sort_values('Distance_From_MA_%', ascending=True)
    
    above_charts = []
    for i in range(0, len(above_df), stocks_per_chart):
        chunk = above_df.iloc[i:i + stocks_per_chart]
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(chunk['Symbol'], chunk['Distance_From_MA_%'], color='#2ecc71')
        ax.axhline(0, color='black', linewidth=1, linestyle='--')
        ax.set_xlabel("Stock Symbol", fontsize=10)
        ax.set_ylabel("Distance from 200-day MA (%)", fontsize=10)
        ax.set_title(f"Indian Stocks Above 200-day MA (Group {i//stocks_per_chart + 1})", fontsize=12, pad=15)
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'+{height:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        above_charts.append(fig)
    
    below_charts = []
    for i in range(0, len(below_df), stocks_per_chart):
        chunk = below_df.iloc[i:i + stocks_per_chart]
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(chunk['Symbol'], chunk['Distance_From_MA_%'], color='#e74c3c')
        ax.axhline(0, color='black', linewidth=1, linestyle='--')
        ax.set_xlabel("Stock Symbol", fontsize=10)
        ax.set_ylabel("Distance from 200-day MA (%)", fontsize=10)
        ax.set_title(f"Indian Stocks Below 200-day MA (Group {i//stocks_per_chart + 1})", fontsize=12, pad=15)
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%', ha='center', va='top')
        
        plt.tight_layout()
        below_charts.append(fig)
    
    return above_charts, below_charts

def main():
    st.title("Indian Stock Market Health Analysis")
    st.write("Analysis of NSE stocks relative to their 200-day Moving Average")
    
    col1, col2 = st.columns(2)
    with col1:
        stocks_per_page = st.selectbox("Stocks per chart", [10, 15, 20, 25, 30], index=1)
    with col2:
        ma_period = st.selectbox("Moving Average Period (days)", [50, 100, 200], index=2)
    
    with st.spinner("Fetching data and calculating moving averages..."):
        tickers = get_nifty_tickers()
        df = get_stocks_below_ma(tickers, ma_period)
    
    if df.empty:
        st.error("No data available. Please check your internet connection or try again later.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Stocks", len(df))
    with col2:
        st.metric("Stocks Above MA", len(df[df['Distance_From_MA_%'] >= 0]))
    with col3:
        st.metric("Stocks Below MA", len(df[df['Distance_From_MA_%'] < 0]))

    above_charts, below_charts = create_charts(df, stocks_per_page)
    
    if above_charts:
        st.subheader("Stocks Trading Above MA")
        tabs_above = st.tabs([f"Group {i+1}" for i in range(len(above_charts))])
        for tab, chart in zip(tabs_above, above_charts):
            with tab:
                st.pyplot(chart)
    
    if below_charts:
        st.subheader("Stocks Trading Below MA")
        tabs_below = st.tabs([f"Group {i+1}" for i in range(len(below_charts))])
        for tab, chart in zip(tabs_below, below_charts):
            with tab:
                st.pyplot(chart)
    
    st.subheader("Detailed Stock Data")
    col1, col2 = st.columns(2)
    with col1:
        filter_option = st.selectbox("Filter by", ["All", "Above MA", "Below MA"])
    with col2:
        sort_by = st.selectbox("Sort by", ["Distance_From_MA_%", "Current_Price", "Volume", "Price_Change_%"])
    
    filtered_df = df
    if filter_option == "Above MA":
        filtered_df = df[df['Distance_From_MA_%'] >= 0]
    elif filter_option == "Below MA":
        filtered_df = df[df['Distance_From_MA_%'] < 0]
    
    st.dataframe(filtered_df.sort_values(sort_by, ascending=False))

if __name__ == "__main__":
    main()
