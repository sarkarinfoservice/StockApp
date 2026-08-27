import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(page_title="Pro Stock Technical Analyzer", page_icon="📈", layout="centered")

st.title("📈 Pro Stock Technical Analyzer")
st.markdown("Advanced Technical Analysis, Market Scanner, Buy/Sell Signals & Beginner Guide.")

# ==========================================
# 🔍 SMART MARKET SCANNER SECTION
# ==========================================
st.markdown("### 🔍 Smart Market Scanner")
st.write("Janiye aaj kin popular stocks mein tezi (Uptrend) ban rahi hai.")

if st.button("🚀 Find Trending Stocks", use_container_width=True):
    # Top 20 Popular Indian Stocks for Scanning
    scan_list = [
        "RELIANCE.NS", "TATAMOTORS.NS", "SBIN.NS", "HDFCBANK.NS", "ZOMATO.NS", 
        "IRFC.NS", "HAL.NS", "SUZLON.NS", "TCS.NS", "INFY.NS", 
        "ITC.NS", "ICICIBANK.NS", "BHARTIARTL.NS", "BAJFINANCE.NS", "LT.NS", 
        "M&M.NS", "NTPC.NS", "TATASTEEL.NS", "BHEL.NS", "BEL.NS"
    ]
    
    trending_stocks = []
    
    # Progress bar for PRO feel
    my_bar = st.progress(0, text="Market scan shuru ho raha hai...")
    
    for i, stock in enumerate(scan_list):
        my_bar.progress((i + 1) / len(scan_list), text=f"Scanning {stock.replace('.NS', '')}...")
        try:
            # Fetch 6 months data for quick scanning
            df_scan = yf.download(stock, period="6mo", progress=False)
            if df_scan.empty: continue
            
            if isinstance(df_scan.columns, pd.MultiIndex):
                df_scan.columns = df_scan.columns.get_level_values(0)
                
            close_scan = df_scan['Close']
            current_price = float(close_scan.iloc[-1])
            
            # Moving Average (20 DMA)
            dma20 = float(close_scan.rolling(20).mean().iloc[-1])
            
            # RSI
            delta = close_scan.diff()
            gain = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
            loss = (-1 * delta.clip(upper=0)).ewm(com=13, adjust=False).mean()
            rs = gain / loss
            rsi = float((100 - (100 / (1 + rs))).iloc[-1])
            
            # MACD
            ema12 = close_scan.ewm(span=12, adjust=False).mean()
            ema26 = close_scan.ewm(span=26, adjust=False).mean()
            macd = ema12 - ema26
            macd_signal = macd.ewm(span=9, adjust=False).mean()
            current_macd = float(macd.iloc[-1])
            current_signal = float(macd_signal.iloc[-1])
            
            # 🚀 CONDITION FOR TRENDING STOCK: 
            # Price upar ho + MACD bullish ho + RSI safe zone (40-70) me ho
            if (current_price > dma20) and (current_macd > current_signal) and (40 <= rsi <= 70):
                trending_stocks.append({
                    "Symbol": stock.replace(".NS", ""),
                    "Price (₹)": round(current_price, 2),
                    "RSI": round(rsi, 1),
                    "Trend": "Bullish 🟢"
                })
        except Exception as e:
            pass # Ignore errors for individual stocks during bulk scan
            
    my_bar.empty() # Hide progress bar when done
    
    # Show Results
    if trending_stocks:
        st.success(f"🎉 Great! {len(trending_stocks)} Trending Stocks mile hain.")
        df_results = pd.DataFrame(trending_stocks)
        # Set Symbol as index so it looks clean in table
        st.dataframe(df_results.set_index("Symbol"), use_container_width=True)
        st.info("💡 **PRO TIP:** Upar list me se koi bhi Symbol copy karein aur niche wale box me daal kar uska poora analysis (Target & Stoploss) check karein!")
    else:
        st.warning("🔴 Aaj in top stocks mein koi clear buy signal nahi mila. Market shant ya downtrend mein ho sakti hai.")

st.divider()

# ==========================================
# 📊 MAIN STOCK ANALYZER SECTION
# ==========================================
st.markdown("### 🔍 Full Stock Analysis")

# --- USER INPUTS ---
trading_style = st.selectbox("Trading Style Select Karein:", 
                             ["Swing (Weeks to Months)", "Intraday (Same Day) & BTST", "Long Term (1-5 Years)"])

col1, col2 = st.columns(2)
with col1:
    exchange = st.selectbox("Exchange", ["NSE", "BSE"])
with col2:
    raw_symbol = st.text_input("Stock Symbol (e.g., ZOMATO)", value="").strip().upper()

col3, col4 = st.columns(2)
with col3:
    investment = st.number_input("New Investment Amount (₹) [Optional]", min_value=0.0, value=0.0, step=1000.0)
with col4:
    purchase_price = st.number_input("Apna Buy Price Dalein (₹) [Optional]", min_value=0.0, value=0.0, step=10.0)

if st.button("📊 Analyze This Stock", use_container_width=True):
    if not raw_symbol:
        st.error("Kripya koi ek Stock Symbol dalein!")
    else:
        # Format symbol for yfinance
        symbol = raw_symbol
        if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
            symbol += ".NS" if exchange == "NSE" else ".BO"

        # --- DYNAMIC SETTINGS BASED ON TRADING STYLE ---
        if trading_style == "Intraday (Same Day) & BTST":
            dl_period, dl_interval = "5d", "15m"
            ma1, ma2, ma3 = 9, 21, 50
            t1, t2, t3 = 1.01, 1.02, 1.03  # 1%, 2%, 3% Targets
            sl_pct = 0.99  # 1% Stoploss
            tf_label = "15-Min"
            supp_window = 20
            hl_label = "5-Day"
        elif trading_style == "Long Term (1-5 Years)":
            dl_period, dl_interval = "5y", "1wk"
            ma1, ma2, ma3 = 20, 50, 200
            t1, t2, t3 = 1.50, 2.00, 3.00  # 50%, 100%, 200% Targets
            sl_pct = 0.85  # 15% Stoploss
            tf_label = "Weekly"
            supp_window = 52
            hl_label = "5-Year"
        else:  # Swing (Default)
            dl_period, dl_interval = "1y", "1d"
            ma1, ma2, ma3 = 20, 50, 200
            t1, t2, t3 = 1.10, 1.15, 1.20  # 10%, 15%, 20% Targets
            sl_pct = 0.95  # 5% Stoploss
            tf_label = "Daily"
            supp_window = 30
            hl_label = "52-Week"

        with st.spinner(f"Fetching {tf_label} data for {symbol}..."):
            try:
                # Fetch Data dynamically
                df = yf.download(symbol, period=dl_period, interval=dl_interval, progress=False)
                
                if df.empty:
                    st.error("❌ Data nahi mila. Symbol aur Exchange check karein.")
                else:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)

                    # --- 1. BASIC CALCULATIONS ---
                    close = df['Close']
                    current_price = float(close.iloc[-1])
                    
                    # Moving Averages (Dynamic)
                    sma1 = float(close.rolling(ma1).mean().iloc[-1]) if len(close) >= ma1 else current_price
                    sma2 = float(close.rolling(ma2).mean().iloc[-1]) if len(close) >= ma2 else current_price
                    sma3 = float(close.rolling(ma3).mean().iloc[-1]) if len(close) >= ma3 else current_price
                    
                    ema1 = float(close.ewm(span=ma1, adjust=False).mean().iloc[-1])
                    ema2 = float(close.ewm(span=ma2, adjust=False).mean().iloc[-1])

                    # RSI Calculation
                    delta = close.diff()
                    gain = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
                    loss = (-1 * delta.clip(upper=0)).ewm(com=13, adjust=False).mean()
                    rs = gain / loss
                    rsi = float((100 - (100 / (1 + rs))).iloc[-1])
                    
                    if rsi > 70:
                        rsi_status = "Overbought 🔴"
                    elif rsi < 30:
                        rsi_status = "Oversold 🟢"
                    else:
                        rsi_status = "Neutral 🟡"

                    # MACD Calculation
                    ema12 = close.ewm(span=12, adjust=False).mean()
                    ema26 = close.ewm(span=26, adjust=False).mean()
                    macd = ema12 - ema26
                    macd_signal = macd.ewm(span=9, adjust=False).mean()
                    current_macd = float(macd.iloc[-1])
                    current_signal = float(macd_signal.iloc[-1])
                    is_macd_bullish = current_macd > current_signal

                    # Support & Resistance (Dynamic Window)
                    recent_data = df.tail(supp_window)
                    support = float(recent_data['Low'].min())
                    resistance = float(recent_data['High'].max())

                    # --- 2. ADVANCED CALCULATIONS ---
                    # Volume Analysis
                    volume = df['Volume']
                    current_volume = float(volume.iloc[-1])
                    avg_volume = float(volume.rolling(ma1).mean().iloc[-1])
                    volume_ratio = (current_volume / avg_volume) if avg_volume > 0 else 1.0
                    is_high_volume = volume_ratio >= 1.3 

                    # Bollinger Bands (20-period)
                    bb_middle = float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else current_price
                    std_20 = float(close.rolling(20).std().iloc[-1]) if len(close) >= 20 else 0
                    bb_upper = bb_middle + (2 * std_20)
                    bb_lower = bb_middle - (2 * std_20)

                    # High / Low Range
                    period_high = float(df['High'].max())
                    period_low = float(df['Low'].min())
                    discount_from_high = ((period_high - current_price) / period_high) * 100

                    # Dynamic Targets & Levels
                    buy_zone = current_price * 0.99
                    strong_buy = support if support < current_price else current_price * sl_pct
                    stop_loss = support * 0.99
                    
                    target_a = current_price * t1
                    target_b = current_price * t2
                    target_c = current_price * t3

                    # --- 3. TREND LOGIC ---
                    if current_price > sma2 and sma2 > sma3:
                        trend_status = "UPTREND 📈"
                        trend_reason = f"Price {ma2} SMA ke upar hai aur trend positive hai."
                    elif current_price < sma2 and sma2 < sma3:
                        trend_status = "DOWNTREND 📉"
                        trend_reason = f"Price {ma2} aur {ma3} SMA ke niche trade kar raha hai."
                    else:
                        trend_status = "SIDEWAYS ↔️"
                        trend_reason = "Price range bound hai (na clear upar na niche)."

                    # --- 4. FRESH BUY SIGNAL LOGIC ---
                    is_ema_bullish = ema1 > ema2
                    
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
                        signal_msg = f"Stock lower band ya RSI oversold zone ke paas hai. Support pe accumulate kar sakte hain."
                    elif current_price >= bb_upper or rsi > 70:
                        signal_box = st.warning
                        signal_title = "🔴 WAIT: OVERBOUGHT ZONE"
                        signal_msg = f"Stock Upper Band ke paas hai aur RSI high hai. Fresh buy mat karein, dip ka wait karein."
                    else:
                        signal_box = st.error
                        signal_title = "🔴 AVOID / WAIT: NO SIGNAL"
                        signal_msg = f"{trend_reason} Abhi koi clear buy signal nahi hai."

                    # --- 5. UI DISPLAY START ---
                    st.subheader(f"Results for {symbol} ({trading_style})")
                    
                    if purchase_price == 0:
                        signal_box(f"**{signal_title}**\n\n{signal_msg}")
                    
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
                        elif pnl_percent >= ((t1-1)*100) and (rsi > 70 or current_price >= bb_upper):
                            hs_box = st.success
                            hs_title = "🟢 BOOK PROFIT (Sell)"
                            hs_msg = f"Aapko Target hit ho gaya hai aur stock Overbought hai. Profit book kar sakte hain."
                        elif "DOWNTREND" in trend_status:
                            hs_box = st.warning
                            hs_title = "🔴 SELL (Trend Weak)"
                            hs_msg = "Market ka main trend negative ho chuka hai. Exit karna safe rahega."
                        else:
                            hs_box = st.info
                            hs_title = "🟡 HOLD"
                            hs_msg = "Technical indicators abhi safe hain. Target tak hold rakh sakte hain."
                            
                        hs_box(f"**Action:** {hs_title}\n\n**Reason:** {hs_msg}")

                    st.divider()
                    
                    m1, m2 = st.columns(2)
                    m1.metric("Current Price", f"₹{current_price:.2f}")
                    m2.metric("Trend", trend_status.replace("📈", "").replace("📉", "").replace("↔️", ""))
                    
                    m3, m4 = st.columns(2)
                    m3.metric("RSI (14)", f"{rsi:.1f}")
                    m4.metric("Volume Vs Avg", f"{volume_ratio:.1f}x")

                    st.divider()

                    col_left, col_right = st.columns(2)
                    
                    with col_left:
                        st.markdown(f"### 📊 Action Zones ({tf_label})")
                        st.write(f"**Buy Zone:** ₹{buy_zone:.2f} - ₹{current_price:.2f}")
                        st.write(f"**Strong Buy:** ₹{strong_buy:.2f}")
                        st.write(f"**Stop-Loss:** ₹{stop_loss:.2f}")
                        
                        with st.expander("💡 Iska kya matlab hai?"):
                            st.info("""
                            **Buy Zone:** Safe range jahan tak stock ko buying ke liye consider kiya ja sakta hai.\n
                            **Strong Buy:** Support level ke paas sasta price jahan risk sabse kam hota hai.\n
                            **Stop-Loss:** Bada nuksan rokne ke liye is level par exit kar lena chahiye.
                            """)
                        
                        st.markdown("### 🎯 Targets")
                        st.write(f"**Target 1 ({(t1-1)*100:.0f}%):** ₹{target_a:.2f}")
                        st.write(f"**Target 2 ({(t2-1)*100:.0f}%):** ₹{target_b:.2f}")
                        st.write(f"**Target 3 ({(t3-1)*100:.0f}%):** ₹{target_c:.2f}")

                        with st.expander("💡 Target ka matlab?"):
                            st.info("Kharidne ke baad in levels par aane par aap apna profit book (sell) kar sakte hain.")

                        st.markdown(f"### 🏆 {hl_label} Range")
                        st.write(f"**High:** ₹{period_high:.2f}")
                        st.write(f"**Low:** ₹{period_low:.2f}")
                        st.write(f"**Discount:** {discount_from_high:.1f}%")
                        
                        with st.expander("💡 Range ka matlab?"):
                            st.info("Yeh batata hai ki stock apne pichle highest price se abhi kitna sasta (discounted) mil raha hai.")

                    with col_right:
                        st.markdown("### 📉 Technical Indicators")
                        st.write(f"**RSI (14):** {rsi:.1f} ({rsi_status})")
                        macd_status = "Bullish 🟢" if is_macd_bullish else "Bearish 🔴"
                        st.write(f"**MACD:** {macd_status}")
                        st.write(f"**Support:** ₹{support:.2f}")
                        st.write(f"**Resistance:** ₹{resistance:.2f}")
                        
                        with st.expander("💡 Technicals kya batate hain?"):
                            macd_desc = "**MACD Bullish 🟢:** Buying momentum hai, stock upar ja sakta hai." if is_macd_bullish else "**MACD Bearish 🔴:** Selling pressure hai, stock niche gir sakta hai."
                            st.info(f"""
                            **RSI:** 70 ke upar gaya matlab stock mahenga (Overbought) hai. 30 ke niche gaya matlab sasta (Oversold) hai.\n
                            {macd_desc}\n
                            **Support:** Lower level jahan se price niche girna band hota hai.\n
                            **Resistance:** Upper level jahan se price takra kar rukta hai.
                            """)
                        
                        st.markdown("### 📈 Moving Averages")
                        st.write(f"**{ma1} EMA:** ₹{ema1:.2f} | **{ma1} SMA:** ₹{sma1:.2f}")
                        st.write(f"**{ma2} EMA:** ₹{ema2:.2f} | **{ma2} SMA:** ₹{sma2:.2f}")
                        st.write(f"**{ma3} SMA:** ₹{sma3:.2f}")
                        
                        with st.expander("💡 Averages ka kya kaam hai?"):
                            st.info(f"Is mode mein system automatically {ma1}, {ma2}, aur {ma3} period ke averages use kar raha hai. Current price agar Averages ke UPAR ho, toh stock strong Uptrend mein maana jata hai.")

                        st.markdown("### 🌀 Bollinger Bands")
                        st.write(f"**Upper Band:** ₹{bb_upper:.2f}")
                        st.write(f"**Lower Band:** ₹{bb_lower:.2f}")
                        
                        with st.expander("💡 Bollinger Bands ka matlab?"):
                            st.info("""
                            **Lower Band:** Price iske paas ho toh stock bahut sasta (Oversold) hai.\n
                            **Upper Band:** Price iske paas ho toh stock mahenga (Overbought) hai.
                            """)

                    if investment > 0 and purchase_price == 0:
                        st.divider()
                        shares = int(investment // current_price)
                        actual_inv = shares * current_price
                        st.markdown("### 💰 Investment Plan")
                        st.success(f"Capital: **₹{investment:.2f}** | Shares: **{shares}** | Used: **₹{actual_inv:.2f}** | Exp. Profit (T1): **₹{(target_a - current_price) * shares:.2f}**")

            except Exception as e:
                st.error(f