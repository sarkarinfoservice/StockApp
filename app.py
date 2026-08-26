import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(page_title="Stock Technical Analyzer", page_icon="📈", layout="centered")

st.title("📈 Pro Stock Technical Analyzer")
st.markdown("Enter stock symbol and your buy price to get Buy, Hold or Sell signals.")

# User Inputs - Row 1
col1, col2 = st.columns(2)
with col1:
    exchange = st.selectbox("Exchange", ["NSE", "BSE"])
with col2:
    raw_symbol = st.text_input("Stock Symbol (e.g., RELIANCE)", value="ASTRAMICRO").strip().upper()

# User Inputs - Row 2
col3, col4 = st.columns(2)
with col3:
    investment = st.number_input("New Investment Amount (₹) [Optional]", min_value=0.0, value=0.0, step=1000.0)
with col4:
    purchase_price = st.number_input("Apna Buy Price Dalein (₹) [Optional]", min_value=0.0, value=0.0, step=10.0, help="Agar aapne ye stock pehle se kharida hai toh apna price dalein.")

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
                    
                    # DMA
                    dma20 = float(close.rolling(20).mean().iloc[-1])
                    dma50 = float(close.rolling(50).mean().iloc[-1])
                    dma100 = float(close.rolling(100).mean().iloc[-1])
                    dma200 = float(close.rolling(200).mean().iloc[-1])
                    
                    # EMA
                    ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
                    ema50 = float(close.ewm(span=50, adjust=False).mean().iloc[-1])

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

                    # --- TREND LOGIC ---
                    if current_price > dma50 and dma50 > dma200:
                        trend_status = "UPTREND 📈"
                        trend_reason = "Kyunki price 50 DMA ke upar hai aur 50 DMA 200 DMA ke upar hai."
                    elif current_price < dma50 and dma50 < dma200:
                        trend_status = "DOWNTREND 📉"
                        trend_reason = "Kyunki price lagatar 50 aur 200 DMA ke niche trade kar raha hai."
                    else:
                        trend_status = "SIDEWAYS ↔️"
                        trend_reason = "Kyunki price range bound hai (na clear upar na niche)."
                    
                    # --- FRESH BUY SIGNAL LOGIC ---
                    is_ema_bullish = ema20 > ema50
                    is_macd_bullish = current_macd > current_signal
                    
                    if "UPTREND" in trend_status and is_ema_bullish and is_macd_bullish and (40 <= rsi <= 70):
                        signal_box = st.success
                        signal_title = "🟢 FRESH BUY: STRONG TREND"
                        signal_msg = f"{trend_reason} EMA aur MACD bhi Bullish hain."
                    elif rsi < 30:
                        signal_box = st.info
                        signal_title = "🟡 ACCUMULATE: OVERSOLD"
                        signal_msg = f"{trend_reason} Lekin stock bahut gir chuka hai (RSI < 30). Support ke paas kharid sakte hain."
                    elif is_macd_bullish and rsi > 70:
                        signal_box = st.warning
                        signal_title = "🔴 WAIT: OVERBOUGHT"
                        signal_msg = f"{trend_reason} Par stock abhi thoda mahenga (Overbought) hai. Dip ka wait karein."
                    else:
                        signal_box = st.error
                        signal_title = "🔴 AVOID: NO FRESH BUY"
                        signal_msg = f"{trend_reason} Trend weak hai, abhi fresh entry na lein."

                    # --- UI DISPLAY START ---
                    st.subheader(f"Results for {symbol}")
                    
                    # Display Fresh Buy Signal
                    if purchase_price == 0:
                        signal_box(f"**{signal_title}**\n\n{signal_msg}")
                    
                    # --- HOLD OR SELL LOGIC (If user bought the stock) ---
                    if purchase_price > 0:
                        pnl_percent = ((current_price - purchase_price) / purchase_price) * 100
                        pnl_amount = current_price - purchase_price
                        
                        st.markdown("### 💼 Your Portfolio Status")
                        if pnl_percent > 0:
                            st.success(f"**Profit:** ₹{pnl_amount:.2f} per share (+{pnl_percent:.2f}%)")
                        else:
                            st.error(f"**Loss:** ₹{abs(pnl_amount):.2f} per share ({pnl_percent:.2f}%)")
                        
                        # Decision Logic
                        if current_price < purchase_price * 0.95 or current_price < stop_loss:
                            hs_box = st.error
                            hs_title = "🔴 SELL (Stop-Loss Hit)"
                            hs_msg = "Stock aapke buy price ya technical support se kafi niche aa gaya hai. Loss aur badhne se pehle exit karna safe rahega."
                        elif pnl_percent > 10 and rsi > 70 and not is_macd_bullish:
                            hs_box = st.success
                            hs_title = "🟢 BOOK PROFIT (Sell)"
                            hs_msg = "Aapko accha profit ho raha hai aur indicators bata rahe hain ki stock gir sakta hai (Overbought). Profit book kar lijiye."
                        elif "DOWNTREND" in trend_status:
                            hs_box = st.warning
                            hs_title = "🔴 SELL (Trend Reversed)"
                            hs_msg = "Market ka trend negative ho chuka hai. Position hold karna risky ho sakta hai."
                        else:
                            hs_box = st.info
                            hs_title = "🟡 HOLD"
                            hs_msg = "Trend aur indicators abhi theek hain. Aap apne stock ko aaram se hold kar sakte hain."
                            
                        hs_box(f"**Action:** {hs_title}\n\n**Reason:** {hs_msg}")

                    st.divider()
                    
                    # Metrics
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Current Price", f"₹{current_price:.2f}")
                    m2.metric("Trend", trend_status.replace("📈", "").replace("📉", "").replace("↔️", ""))
                    m3.metric("RSI", f"{rsi:.2f}")

                    st.divider()

                    col_left, col_right = st.columns(2)
                    
                    with col_left:
                        st.markdown("### 📊 Action Zones")
                        st.write(f"**Buy Zone:** ₹{buy_zone:.2f} - ₹{current_price:.2f}")
                        st.write(f"**Strong Buy:** ₹{strong_buy:.2f}")
                        st.write(f"**Stop-Loss:** ₹{stop_loss:.2f}")
                        
                        st.markdown("### 🎯 Targets")
                        st.write(f"**Target 1 (10%):** ₹{target_10:.2f}")
                        st.write(f"**Target 2 (15%):** ₹{target_15:.2f}")

                    with col_right:
                        st.markdown("### 📉 Technicals")
                        st.write(f"**MACD:** {'Bullish 🟢' if current_macd > current_signal else 'Bearish 🔴'}")
                        st.write(f"**Support:** ₹{support:.2f}")
                        st.write(f"**Resistance:** ₹{resistance:.2f}")
                        
                        st.markdown("### 📈 Moving Averages")
                        st.write(f"**20 EMA:** ₹{ema20:.2f} | **20 DMA:** ₹{dma20:.2f}")
                        st.write(f"**50 EMA:** ₹{ema50:.2f} | **50 DMA:** ₹{dma50:.2f}")

                    if investment > 0 and purchase_price == 0:
                        st.divider()
                        shares = int(investment // current_price)
                        actual_inv = shares * current_price
                        st.markdown("### 💰 Investment Plan")
                        st.success(f"Capital: **₹{investment:.2f}** | Shares: **{shares}** | Amount Used: **₹{actual_inv:.2f}** | Exp. Profit: **₹{(target_10 - current_price) * shares:.2f}**")

            except Exception as e:
                st.error(f"Error aayi: {e}")

st.caption("Disclaimer: This tool is for educational purposes only. Do your own research before investing.")
