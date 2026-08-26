import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(page_title="Pro Stock Technical Analyzer", page_icon="📈", layout="centered")

st.title("📈 Pro Stock Technical Analyzer (Ultimate Edition)")
st.markdown("Advanced Technical Analysis, Buy/Sell Signals, Portfolio Tracker & Beginner Guide.")

# --- USER INPUTS ---
col1, col2 = st.columns(2)
with col1:
    exchange = st.selectbox("Exchange", ["NSE", "BSE"])
with col2:
    raw_symbol = st.text_input("Stock Symbol (e.g., RELIANCE, TATAMOTORS)", value="ASTRAMICRO").strip().upper()

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

        with st.spinner(f"Fetching complete technical data for {symbol}..."):
            try:
                # Fetch 1 year of data
                df = yf.download(symbol, period="1y", progress=False)
                
                if df.empty:
                    st.error("❌ Data nahi mila. Symbol aur Exchange check karein.")
                else:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)

                    # --- 1. BASIC CALCULATIONS ---
                    close = df['Close']
                    current_price = float(close.iloc[-1])
                    
                    # Moving Averages (DMA & EMA)
                    dma20 = float(close.rolling(20).mean().iloc[-1])
                    dma50 = float(close.rolling(50).mean().iloc[-1])
                    dma100 = float(close.rolling(100).mean().iloc[-1])
                    dma200 = float(close.rolling(200).mean().iloc[-1])
                    
                    ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
                    ema50 = float(close.ewm(span=50, adjust=False).mean().iloc[-1])

                    # RSI Calculation
                    delta = close.diff()
                    gain = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
                    loss = (-1 * delta.clip(upper=0)).ewm(com=13, adjust=False).mean()
                    rs = gain / loss
                    rsi = float((100 - (100 / (1 + rs))).iloc[-1])

                    # MACD Calculation
                    ema12 = close.ewm(span=12, adjust=False).mean()
                    ema26 = close.ewm(span=26, adjust=False).mean()
                    macd = ema12 - ema26
                    macd_signal = macd.ewm(span=9, adjust=False).mean()
                    current_macd = float(macd.iloc[-1])
                    current_signal = float(macd_signal.iloc[-1])
                    is_macd_bullish = current_macd > current_signal

                    # Support & Resistance (30 Days)
                    recent_30 = df.tail(30)
                    support = float(recent_30['Low'].min())
                    resistance = float(recent_30['High'].max())

                    # --- 2. ADVANCED CALCULATIONS ---
                    # Volume Analysis
                    volume = df['Volume']
                    current_volume = float(volume.iloc[-1])
                    avg_volume_20 = float(volume.rolling(20).mean().iloc[-1])
                    volume_ratio = (current_volume / avg_volume_20) if avg_volume_20 > 0 else 1.0
                    is_high_volume = volume_ratio >= 1.3  # 30% or more volume than 20-day average

                    # Bollinger Bands (20-period, 2 std dev)
                    bb_middle = dma20
                    std_20 = float(close.rolling(20).std().iloc[-1])
                    bb_upper = bb_middle + (2 * std_20)
                    bb_lower = bb_middle - (2 * std_20)

                    # 52-Week High / Low
                    high_52w = float(df['High'].max())
                    low_52w = float(df['Low'].min())
                    discount_from_high = ((high_52w - current_price) / high_52w) * 100

                    # Targets & Levels
                    buy_zone = current_price * 0.98
                    strong_buy = support if support < current_price else current_price * 0.95
                    stop_loss = support * 0.97
                    
                    target_10 = current_price * 1.10
                    target_15 = current_price * 1.15
                    target_20 = current_price * 1.20

                    # --- 3. TREND LOGIC ---
                    if current_price > dma50 and dma50 > dma200:
                        trend_status = "UPTREND 📈"
                        trend_reason = "Price 50 DMA ke upar hai aur 50 DMA 200 DMA ke upar chal raha hai."
                    elif current_price < dma50 and dma50 < dma200:
                        trend_status = "DOWNTREND 📉"
                        trend_reason = "Price lagatar 50 aur 200 DMA ke niche trade kar raha hai."
                    else:
                        trend_status = "SIDEWAYS ↔️"
                        trend_reason = "Price range bound hai (na clear upar na niche)."

                    # --- 4. FRESH BUY SIGNAL LOGIC ---
                    is_ema_bullish = ema20 > ema50
                    
                    if "UPTREND" in trend_status and is_ema_bullish and is_macd_bullish and (40 <= rsi <= 70):
                        if is_high_volume:
                            signal_box = st.success
                            signal_title = "🟢 STRONG BUY: HIGH VOLUME BREAKOUT!"
                            signal_msg = f"{trend_reason} High volume ({volume_ratio:.1f}x) ke sath breakout mila hai."
                        else:
                            signal_box = st.success
                            signal_title = "🟢 FRESH BUY: UPTREND CONFIRMED"
                            signal_msg = f"{trend_reason} EMA aur MACD dono Bullish zone mein hain."
                    elif rsi < 35 or current_price <= bb_lower:
                        signal_box = st.info
                        signal_title = "🟡 ACCUMULATE: OVERSOLD / BOTTOM ZONE"
                        signal_msg = f"Stock lower Bollinger band ya RSI oversold zone ke paas hai. Support pe chhote quantity me accumulation kar sakte hain."
                    elif current_price >= bb_upper or rsi > 70:
                        signal_box = st.warning
                        signal_title = "🔴 WAIT: OVERBOUGHT ZONE"
                        signal_msg = f"Stock Upper Bollinger Band ke paas hai aur RSI high hai. Fresh buy mat karein, dip ka wait karein."
                    else:
                        signal_box = st.error
                        signal_title = "🔴 AVOID / WAIT: NO SIGNAL"
                        signal_msg = f"{trend_reason} Abhi koi clear buy signal nahi hai."

                    # --- 5. UI DISPLAY START ---
                    st.subheader(f"Results for {symbol}")
                    
                    # Display Signal Box (If user has NOT bought yet)
                    if purchase_price == 0:
                        signal_box(f"**{signal_title}**\n\n{signal_msg}")
                    
                    # Portfolio Status Box (If user HAS bought)
                    if purchase_price > 0:
                        pnl_percent = ((current_price - purchase_price) / purchase_price) * 100
                        pnl_amount = current_price - purchase_price
                        
                        st.markdown("### 💼 Your Portfolio Status")
                        if pnl_percent > 0:
                            st.success(f"**Profit:** ₹{pnl_amount:.2f} per share (+{pnl_percent:.2f}%)")
                        else:
                            st.error(f"**Loss:** ₹{abs(pnl_amount):.2f} per share ({pnl_percent:.2f}%)")
                        
                        if current_price < purchase_price * 0.95 or current_price < stop_loss:
                            hs_box = st.error
                            hs_title = "🔴 SELL (Stop-Loss Hit)"
                            hs_msg = "Stock buy price aur major support se niche chala gaya hai. Loss cut karna safe hoga."
                        elif pnl_percent >= 10 and (rsi > 70 or current_price >= bb_upper):
                            hs_box = st.success
                            hs_title = "🟢 BOOK PROFIT (Sell)"
                            hs_msg = f"Aapko +{pnl_percent:.1f}% ka profit ho raha hai aur stock Overbought zone mein hai. Partial/Full profit book kar sakte hain."
                        elif "DOWNTREND" in trend_status:
                            hs_box = st.warning
                            hs_title = "🔴 SELL (Trend Weak)"
                            hs_msg = "Market ka main trend negative ho chuka hai. Exit karna safe rahega."
                        else:
                            hs_box = st.info
                            hs_title = "🟡 HOLD"
                            hs_msg = "Technical indicators abhi safe hain. Target 1 tak hold rakh sakte hain."
                            
                        hs_box(f"**Action:** {hs_title}\n\n**Reason:** {hs_msg}")

                    st.divider()
                    
                    # Top Metrics
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Current Price", f"₹{current_price:.2f}")
                    m2.metric("Trend", trend_status.replace("📈", "").replace("📉", "").replace("↔️", ""))
                    m3.metric("RSI (14)", f"{rsi:.1f}")
                    m4.metric("Volume Vs Avg", f"{volume_ratio:.1f}x")

                    st.divider()

                    col_left, col_right = st.columns(2)
                    
                    with col_left:
                        st.markdown("### 📊 Action Zones")
                        st.write(f"**Buy Zone:** ₹{buy_zone:.2f} - ₹{current_price:.2f}")
                        st.write(f"**Strong Buy:** ₹{strong_buy:.2f}")
                        st.write(f"**Stop-Loss:** ₹{stop_loss:.2f}")
                        
                        with st.expander("💡 Iska kya matlab hai?"):
                            st.info("""
                            **Buy Zone:** Safe range jahan tak stock ko buying ke liye consider kiya ja sakta hai.\n
                            **Strong Buy:** Support level ke paas sasta price jahan risk sabse kam hota hai.\n
                            **Stop-Loss:** Bada nuksan rokne ke liye auto-exit point.
                            """)
                        
                        st.markdown("### 🎯 Targets")
                        st.write(f"**Target 1 (10%):** ₹{target_10:.2f}")
                        st.write(f"**Target 2 (15%):** ₹{target_15:.2f}")
                        st.write(f"**Target 3 (20%):** ₹{target_20:.2f}")
                        
                        with st.expander("💡 Target ka matlab?"):
                            st.info("Kharidne ke baad in levels par aane par aap apna profit book kar sakte hain.")

                        st.markdown("### 🏆 52-Week Range")
                        st.write(f"**52-W High:** ₹{high_52w:.2f}")
                        st.write(f"**52-W Low:** ₹{low_52w:.2f}")
                        st.write(f"**Discount from High:** {discount_from_high:.1f}%")

                        with st.expander("💡 52-Week High/Low ka matlab?"):
                            st.info("Yeh batata hai ki stock apne 1 saal ke highest price se kitna sasta (discounted) mil raha hai.")

                    with col_right:
                        st.markdown("### 📉 Technical Indicators")
                        macd_status = "Bullish 🟢" if is_macd_bullish else "Bearish 🔴"
                        st.write(f"**MACD:** {macd_status}")
                        st.write(f"**Support:** ₹{support:.2f}")
                        st.write(f"**Resistance:** ₹{resistance:.2f}")
                        
                        with st.expander("💡 Technicals kya batate hain?"):
                            if is_macd_bullish:
                                macd_desc = "**MACD Bullish 🟢:** Buying momentum hai, stock upar ja sakta hai."
                            else:
                                macd_desc = "**MACD Bearish 🔴:** Selling pressure hai, stock niche gir sakta hai."
                                
                            st.info(f"""
                            {macd_desc}\n
                            **Support:** Lower level jahan se price niche girna band hota hai.\n
                            **Resistance:** Upper level jahan se price takra kar rukta hai.
                            """)
                        
                        st.markdown("### 📈 Moving Averages")
                        st.write(f"**20 EMA:** ₹{ema20:.2f} | **20 DMA:** ₹{dma20:.2f}")
                        st.write(f"**50 EMA:** ₹{ema50:.2f} | **50 DMA:** ₹{dma50:.2f}")
                        st.write(f"**200 DMA:** ₹{dma200:.2f}")
                        
                        with st.expander("💡 Averages ka kya kaam hai?"):
                            st.info("Current price agar Moving Averages ke UPAR ho, toh stock strong Uptrend mein maana jata hai.")

                        st.markdown("### 🌀 Bollinger Bands & Volume")
                        st.write(f"**BB Upper Band:** ₹{bb_upper:.2f}")
                        st.write(f"**BB Lower Band:** ₹{bb_lower:.2f}")
                        st.write(f"**Volume Status:** {'High Volume 🚀' if is_high_volume else 'Normal Volume ⚖️'}")

                        with st.expander("💡 Bollinger & Volume ka matlab?"):
                            st.info("""
                            **BB Lower Band:** Price iske paas ho toh stock bahut sasta (Oversold) hai.\n
                            **BB Upper Band:** Price iske paas ho toh stock mahenga (Overbought) hai.\n
                            **Volume:** High volume ka matlab bade investors (FIIs/DIIs) active hain.
                            """)

                    if investment > 0 and purchase_price == 0:
                        st.divider()
                        shares = int(investment // current_price)
                        actual_inv = shares * current_price
                        st.markdown("### 💰 Investment Plan")
                        st.success(f"Capital: **₹{investment:.2f}** | Shares: **{shares}** | Amount Used: **₹{actual_inv:.2f}** | Exp. Profit (Target 1): **₹{(target_10 - current_price) * shares:.2f}**")

            except Exception as e:
                st.error(f"Error aayi: {e}")

st.caption("Disclaimer: Yeh tool sirf sikhne (educational purposes) ke liye hai. Investment se pehle apni research zaroor karein.")
