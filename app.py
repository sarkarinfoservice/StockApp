import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(page_title="Stock Technical Analyzer", page_icon="📈", layout="centered")

st.title("📈 Pro Stock Technical Analyzer")
st.markdown("Enter a stock symbol to get instant technical analysis, action zones, and targets.")

# User Inputs
col1, col2 = st.columns(2)
with col1:
    exchange = st.selectbox("Exchange", ["NSE", "BSE"])
with col2:
    raw_symbol = st.text_input("Stock Symbol (e.g., ASTRAMICRO, RELIANCE)", value="ASTRAMICRO").strip().upper()

investment = st.number_input("Investment Amount (₹) [Optional]", min_value=0.0, value=0.0, step=1000.0)

if st.button("🚀 Analyze Stock", use_container_width=True):
    if not raw_symbol:
        st.error("Kripya Stock Symbol dalein!")
    else:
        # Format symbol for yfinance
        symbol = raw_symbol
        if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
            symbol += ".NS" if exchange == "NSE" else ".BO"

        with st.spinner(f"Fetching data for {symbol}..."):
            try:
                # Fetch 1 year of data
                df = yf.download(symbol, period="1y", progress=False)
                
                if df.empty:
                    st.error("❌ Data nahi mila. Symbol aur Exchange check karein.")
                else:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)

                    # --- CALCULATIONS ---
                    close = df['Close']
                    current_price = float(close.iloc[-1])
                    
                    dma20 = float(close.rolling(20).mean().iloc[-1])
                    dma50 = float(close.rolling(50).mean().iloc[-1])
                    dma100 = float(close.rolling(100).mean().iloc[-1])
                    dma200 = float(close.rolling(200).mean().iloc[-1])

                    delta = close.diff()
                    gain = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
                    loss = (-1 * delta.clip(upper=0)).ewm(com=13, adjust=False).mean()
                    rs = gain / loss
                    rsi = float((100 - (100 / (1 + rs))).iloc[-1])

                    ema12 = close.ewm(span=12, adjust=False).mean()
                    ema26 = close.ewm(span=26, adjust=False).mean()
                    macd = ema12 - ema26
                    macd_signal = macd.ewm(span=9, adjust=False).mean()
                    current_macd = float(macd.iloc[-1])
                    current_signal = float(macd_signal.iloc[-1])

                    recent_30 = df.tail(30)
                    support = float(recent_30['Low'].min())
                    resistance = float(recent_30['High'].max())

                    buy_zone = current_price * 0.98
                    strong_buy = support if support < current_price else current_price * 0.95
                    stop_loss = support * 0.97
                    
                    target_10 = current_price * 1.10
                    target_15 = current_price * 1.15
                    target_20 = current_price * 1.20

                    trend = "UPTREND 📈" if current_price > dma50 and dma50 > dma200 else ("DOWNTREND 📉" if current_price < dma50 and dma50 < dma200 else "SIDEWAYS ↔️")
                    
                    verdict = "HOLD"
                    if "UPTREND" in trend:
                        if rsi < 30: verdict = "STRONG BUY 🟢"
                        elif rsi < 70 and current_macd > current_signal: verdict = "BUY 🟢"
                        elif rsi >= 70: verdict = "WAIT (Overbought) 🟡"
                    elif "SIDEWAYS" in trend and rsi < 40:
                        verdict = "ACCUMULATE 🟡"
                    else:
                        verdict = "WAIT / AVOID 🔴"

                    # --- UI DISPLAY ---
                    st.subheader(f"Results for {symbol}")
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Current Price", f"₹{current_price:.2f}")
                    m2.metric("Trend", trend.replace("📈", "").replace("📉", "").replace("↔️", ""))
                    m3.metric("Verdict", verdict.split()[0])

                    st.divider()

                    col_left, col_right = st.columns(2)
                    
                    with col_left:
                        st.markdown("### 📊 Action Zones")
                        st.write(f"**Buy Zone:** ₹{buy_zone:.2f} - ₹{current_price:.2f}")
                        st.write(f"**Strong Buy (Near Support):** ₹{strong_buy:.2f}")
                        st.write(f"**Strict Stop-Loss:** ₹{stop_loss:.2f}")
                        
                        st.markdown("### 🎯 Targets")
                        st.write(f"**Target 1 (10%):** ₹{target_10:.2f}")
                        st.write(f"**Target 2 (15%):** ₹{target_15:.2f}")
                        st.write(f"**Target 3 (20%):** ₹{target_20:.2f}")

                    with col_right:
                        st.markdown("### 📉 Technicals")
                        st.write(f"**RSI (14):** {rsi:.2f}")
                        st.write(f"**MACD:** {'Bullish' if current_macd > current_signal else 'Bearish'}")
                        st.write(f"**Support:** ₹{support:.2f}")
                        st.write(f"**Resistance:** ₹{resistance:.2f}")
                        
                        st.markdown("### 📈 Moving Averages")
                        st.write(f"**20 DMA:** ₹{dma20:.2f}")
                        st.write(f"**50 DMA:** ₹{dma50:.2f}")
                        st.write(f"**200 DMA:** ₹{dma200:.2f}")

                    if investment > 0:
                        st.divider()
                        shares = int(investment // current_price)
                        actual_inv = shares * current_price
                        st.markdown("### 💰 Investment Plan")
                        st.success(f"Capital: **₹{investment:.2f}** | Quantity: **{shares} Shares** | Amount Used: **₹{actual_inv:.2f}** | Expected Profit (10%): **₹{(target_10 - current_price) * shares:.2f}**")

            except Exception as e:
                st.error(f"Error aayi: {e}")

st.caption("Disclaimer: This tool is for educational purposes only. Do your own research before investing.")
