import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Page setup
st.set_page_config(page_title="Pro Stock Technical Analyzer", page_icon="📈", layout="centered")

st.title("📈 Pro Stock Technical Analyzer")
st.markdown("Advanced Technical Analysis, Market Scanner, Buy/Sell Signals & Beginner Guide.")

# ==========================================
# 🔍 SMART MARKET SCANNER SECTION
# ==========================================
st.markdown("### 🔍 Smart Market Scanner")
st.write("Janiye aaj kin popular stocks mein tezi (Uptrend) ban rahi hai.")

if st.button("🚀 Find Trending Stocks", use_container_width=True):
    # Top 40 Stocks List
    scan_list = [
        "RELIANCE.NS", "TATAMOTORS.NS", "SBIN.NS", "HDFCBANK.NS", "ZOMATO.NS", 
        "IRFC.NS", "HAL.NS", "SUZLON.NS", "TCS.NS", "INFY.NS", "ITC.NS", 
        "ICICIBANK.NS", "BHARTIARTL.NS", "BAJFINANCE.NS", "LT.NS", "M&M.NS", 
        "NTPC.NS", "TATASTEEL.NS", "BHEL.NS", "BEL.NS", "ADANIPORTS.NS",
        "ASIANPAINT.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "CIPLA.NS", "COALINDIA.NS",
        "EICHERMOT.NS", "HINDALCO.NS", "INDUSINDBK.NS", "KOTAKBANK.NS", "MARUTI.NS",
        "ONGC.NS", "POWERGRID.NS", "SUNPHARMA.NS", "TATACONSUM.NS", "TITAN.NS",
        "WIPRO.NS", "JIOFIN.NS", "DLF.NS", "TVSMOTOR.NS"
    ]
    
    trending_stocks = []
    
    # Progress bar for scanning
    my_bar = st.progress(0, text="Market scan shuru ho raha hai...")
    
    for i, stock in enumerate(scan_list):
        my_bar.progress((i + 1) / len(scan_list), text=f"Scanning {stock.replace('.NS', '')}...")
        try:
            # Data fetch
            df_scan = yf.download(stock, period="6mo", progress=False)
            if df_scan.empty: 
                continue
                
            if isinstance(df_scan.columns, pd.MultiIndex):
                df_scan.columns = df_scan.columns.get_level_values(0)
            
            close_scan = df_scan['Close']
            current_price = float(close_scan.iloc[-1])
            
            # Moving Average 20
            dma20 = float(close_scan.rolling(20).mean().iloc[-1])
            
            # RSI Calculation
            delta = close_scan.diff()
            gain = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
            loss = (-1 * delta.clip(upper=0)).ewm(com=13, adjust=False).mean()
            rs = gain / loss
            rsi = float((100 - (100 / (1 + rs))).iloc[-1])
            
            # MACD Calculation
            ema12 = close_scan.ewm(span=12, adjust=False).mean()
            ema26 = close_scan.ewm(span=26, adjust=False).mean()
            macd = ema12 - ema26
            macd_signal = macd.ewm(span=9, adjust=False).mean()
            current_macd = float(macd.iloc[-1])
            current_sig = float(macd_signal.iloc[-1])
            
            # RELAXED CONDITION FOR SCANNER (RSI 35 to 75)
            if (current_price > dma20) and (current_macd > current_sig) and (35 <= rsi <= 75):
                trending_stocks.append({
                    "Symbol": stock.replace(".NS", ""),
                    "Price (₹)": round(current_price, 2),
                    "RSI": round(rsi, 1),
                    "Trend": "Bullish 🟢"
                })
        except Exception as e:
            pass # Ignore errors for single stock during scan
            
    my_bar.empty() # Remove progress bar
    
    # Print Scanner Results
    if trending_stocks:
        st.success(f"🎉 Great! {len(trending_stocks)} Trending Stocks mile hain.")
        df_results = pd.DataFrame(trending_stocks)
        st.dataframe(df_results.set_index("Symbol"), use_container_width=True)
        st.info("💡 **PRO TIP:** Upar list me se koi bhi Symbol copy karein aur niche wale box me daal kar uska poora analysis check karein!")
    else:
        st.warning("🔴 Abhi koi clear buy signal nahi mila. Market ka mood thik hone ka wait karein.")

st.divider()

# ==========================================
# 📊 MAIN STOCK ANALYZER SECTION
# ==========================================
st.markdown("### 🔍 Full Stock Analysis")

# --- USER INPUTS ---
trading_style = st.selectbox(
    "Trading Style Select Karein:", 
    ["Swing (Weeks to Months)", "Intraday (Same Day) & BTST", "Long Term (1-5 Years)"]
)

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
        # Format Symbol
        symbol = raw_symbol
        if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
            symbol += ".NS" if exchange == "NSE" else ".BO"

        # --- DYNAMIC SETTINGS based on Trading Style ---
        if trading_style == "Intraday (Same Day) & BTST":
            dl_period = "5d"
            dl_interval = "15m"
            ma1, ma2, ma3 = 9, 21, 50
            t1, t2, t3 = 1.01, 1.02, 1.03
            sl_pct = 0.99
            tf_label = "15-Min"
            supp_window = 20
            hl_label = "5-Day"
        elif trading_style == "Long Term (1-5 Years)":
            dl_period = "5y"
            dl_interval = "1wk"
            ma1, ma2, ma3 = 20, 50, 200
            t1, t2, t3 = 1.50, 2.00, 3.00
            sl_pct = 0.85
            tf_label = "Weekly"
            supp_window = 52
            hl_label = "5-Year"
        else:  
            # Default Swing
            dl_period = "1y"
            dl_interval = "1d"
            ma1, ma2, ma3 = 20, 50, 200
            t1, t2, t3 = 1.10, 1.15, 1.20
            sl_pct = 0.95
            tf_label = "Daily"
            supp_window = 30
            hl_label = "52-Week"

        with st.spinner(f"Fetching {tf_label} data for {symbol}..."):
            try:
                # Fetch Data
                df = yf.download(symbol, period=dl_period, interval=dl_interval, progress=False)
                
                if df.empty:
                    st.error("❌ Data nahi mila. Kripya Symbol aur Exchange check karein.")
                else:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    
                    close = df['Close']
                    current_price = float(close.iloc[-1])
                    
                    # Moving Averages
                    sma1 = float(close.rolling(ma1).mean().iloc[-1]) if len(close) >= ma1 else current_price
                    sma2 = float(close.rolling(ma2).mean().iloc[-1]) if len(close) >= ma2 else current_price
                    sma3 = float(close.rolling(ma3).mean().iloc[-1]) if len(close) >= ma3 else current_price
                    
                    ema1 = float(close.ewm(span=ma1, adjust=False).mean().iloc[-1])
                    ema2 = float(close.ewm(span=ma2, adjust=False).mean().iloc[-1])

                    # VWAP Calculation (Only for Intraday)
                    if trading_style == "Intraday (Same Day) & BTST":
                        df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
                        df['TP_Volume'] = df['Typical_Price'] * df['Volume']
                        df['Cumulative_Volume'] = df.groupby(df.index.date)['Volume'].cumsum()
                        df['Cumulative_TP_Volume'] = df.groupby(df.index.date)['TP_Volume'].cumsum()
                        df['VWAP'] = df['Cumulative_TP_Volume'] / df['Cumulative_Volume']
                        vwap_price = float(df['VWAP'].iloc[-1])

                    # RSI
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

                    # MACD
                    ema12 = close.ewm(span=12, adjust=False).mean()
                    ema26 = close.ewm(span=26, adjust=False).mean()
                    macd = ema12 - ema26
                    macd_sig = macd.ewm(span=9, adjust=False).mean()
                    current_macd = float(macd.iloc[-1])
                    current_signal_line = float(macd_sig.iloc[-1])
                    is_macd_bullish = current_macd > current_signal_line

                    # Support & Resistance
                    recent_data = df.tail(supp_window)
                    support = float(recent_data['Low'].min())
                    resistance = float(recent_data['High'].max())
                    
                    # Volume
                    volume = df['Volume']
                    current_volume = float(volume.iloc[-1])
                    avg_volume = float(volume.rolling(ma1).mean().iloc[-1])
                    volume_ratio = (current_volume / avg_volume) if avg_volume > 0 else 1.0
                    
                    # Bollinger Bands
                    std_20 = float(close.rolling(20).std().iloc[-1]) if len(close) >= 20 else 0
                    bb_middle = float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else current_price
                    bb_upper = bb_middle + (2 * std_20)
                    bb_lower = bb_middle - (2 * std_20)

                    # Range
                    period_high = float(df['High'].max())
                    period_low = float(df['Low'].min())
                    
                    # Targets & Buy Zones
                    buy_zone = current_price * 0.99
                    strong_buy = support if support < current_price else current_price * sl_pct
                    stop_loss = support * 0.99
                    
                    target_a = current_price * t1
                    target_b = current_price * t2
                    target_c = current_price * t3

                    # Trend Logic
                    if current_price > sma2 and sma2 > sma3: 
                        trend_status = "UPTREND 📈"
                        trend_reason = f"Price {ma2} SMA ke upar hai."
                    elif current_price < sma2 and sma2 < sma3: 
                        trend_status = "DOWNTREND 📉"
                        trend_reason = f"Price {ma2} & {ma3} SMA ke niche hai."
                    else: 
                        trend_status = "SIDEWAYS ↔️"
                        trend_reason = "Price range bound hai."

                    # Main Signals
                    if "UPTREND" in trend_status and (ema1 > ema2) and is_macd_bullish and (40 <= rsi <= 70):
                        signal_box = st.success
                        signal_title = "🟢 FRESH BUY"
                        signal_msg = f"{trend_reason} EMA & MACD Bullish hain."
                    elif rsi < 35 or current_price <= bb_lower:
                        signal_box = st.info
                        signal_title = "🟡 ACCUMULATE (Oversold)"
                        signal_msg = "Stock lower band ya support par hai. Dheere-dheere kharid sakte hain."
                    elif current_price >= bb_upper or rsi > 70:
                        signal_box = st.warning
                        signal_title = "🔴 WAIT (Overbought)"
                        signal_msg = "Stock Overbought hai, thoda dip ka wait karein."
                    else:
                        signal_box = st.error
                        signal_title = "🔴 NO SIGNAL"
                        signal_msg = "Abhi clear buy signal nahi hai."

                    # DISPLAY UI
                    st.subheader(f"Results for {symbol} ({trading_style})")
                    
                    if purchase_price == 0: 
                        signal_box(f"**{signal_title}**\n\n{signal_msg}")
                    else:
                        pnl_pct = ((current_price - purchase_price) / purchase_price) * 100
                        pnl_amt = current_price - purchase_price
                        st.markdown("### 💼 Portfolio Status")
                        if pnl_pct > 0: 
                            st.success(f"**Profit:** ₹{pnl_amt:.2f} per share (+{pnl_pct:.2f}%)")
                        else: 
                            st.error(f"**Loss:** ₹{abs(pnl_amt):.2f} per share ({pnl_pct:.2f}%)")

                    st.divider()
                    
                    # Quick Metrics
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Current Price", f"₹{current_price:.2f}")
                    m2.metric("Trend", trend_status.split()[0])
                    m3.metric("RSI (14)", f"{rsi:.1f}")
                    m4.metric("Vol Vs Avg", f"{volume_ratio:.1f}x")
                    
                    st.divider()

                    col_left, col_right = st.columns(2)
                    
                    with col_left:
                        st.markdown(f"### 📊 Action Zones ({tf_label})")
                        st.write(f"**Buy Zone:** ₹{buy_zone:.2f} - ₹{current_price:.2f}")
                        st.write(f"**Strong Buy:** ₹{strong_buy:.2f}")
                        st.write(f"**Stop-Loss:** ₹{stop_loss:.2f}")
                        
                        with st.expander("💡 Iska kya matlab hai?"): 
                            st.info("Buy Zone safe buying range hai. Strong buy support ke paas sasta level hai. Stop-Loss par bada nuksan rokne ke liye bahar nikal jana chahiye.")
                        
                        st.markdown("### 🎯 Targets")
                        st.write(f"**T1:** ₹{target_a:.2f}")
                        st.write(f"**T2:** ₹{target_b:.2f}")
                        st.write(f"**T3:** ₹{target_c:.2f}")
                        
                        with st.expander("💡 Target ka matlab?"): 
                            st.info("Kharidne ke baad in levels par price aane par aap apna thoda-thoda profit book (sell) kar sakte hain.")
                        
                        st.markdown(f"### 🏆 {hl_label} Range")
                        st.write(f"**High:** ₹{period_high:.2f}")
                        st.write(f"**Low:** ₹{period_low:.2f}")
                        
                        with st.expander("💡 Range ka matlab?"): 
                            st.info("Yeh batata hai ki stock apne pichle highest price se abhi kitna sasta (discounted) mil raha hai.")
                    
                    with col_right:
                        st.markdown("### 📉 Technicals")
                        st.write(f"**RSI (14):** {rsi:.1f} ({rsi_status})")
                        
                        macd_display = 'Bullish 🟢' if is_macd_bullish else 'Bearish 🔴'
                        st.write(f"**MACD:** {macd_display}")
                        st.write(f"**Support:** ₹{support:.2f}")
                        st.write(f"**Resistance:** ₹{resistance:.2f}")
                        
                        with st.expander("💡 Technicals kya batate hain?"): 
                            macd_explain = "Buying momentum chal raha hai 🟢" if is_macd_bullish else "Selling pressure chal rahi hai 🔴"
                            st.info(f"**RSI:** 70 se upar (Mahenga/Overbought), 30 se niche (Sasta/Oversold).\n**MACD:** {macd_explain}.\n**Support:** Jaha se price niche girna band karta hai.\n**Resistance:** Jaha se price upar jane mein rukta hai.")
                        
                        st.markdown("### 📈 Moving Averages")
                        st.write(f"**{ma1} EMA:** ₹{ema1:.2f}")
                        st.write(f"**{ma2} EMA:** ₹{ema2:.2f}")
                        st.write(f"**{ma3} SMA:** ₹{sma3:.2f}")
                        
                        # Show VWAP only when Intraday is selected
                        if trading_style == "Intraday (Same Day) & BTST":
                            vwap_trend = "Bullish 🟢" if current_price > vwap_price else "Bearish 🔴"
                            st.write(f"**VWAP (Today):** ₹{vwap_price:.2f} ({vwap_trend})")
                        
                        with st.expander("💡 Averages ka kya kaam hai?"): 
                            vwap_desc = "\n\n**VWAP:** Intraday (Day trading) ka sabse bada indicator. Agar current price VWAP ke UPAR hai, toh stock tezi (Bullish) mein hota hai." if trading_style == "Intraday (Same Day) & BTST" else ""
                            st.info(f"Is mode mein system automatically {ma1}, {ma2}, aur {ma3} period ke averages use kar raha hai. Current price agar Averages ke UPAR ho, toh stock ko strong Uptrend mein maana jata hai.{vwap_desc}")
                        
                        st.markdown("### 🌀 Bollinger Bands")
                        st.write(f"**Upper Band:** ₹{bb_upper:.2f}")
                        st.write(f"**Lower Band:** ₹{bb_lower:.2f}")
                        
                        with st.expander("💡 Bollinger Bands ka matlab?"): 
                            st.info("**Lower Band:** Jab price iske paas ho toh stock bahut sasta (Oversold) hota hai.\n**Upper Band:** Jab price iske paas ho toh stock mahenga (Overbought) hota hai.")

                    # Investment Planner Output
                    if investment > 0 and purchase_price == 0:
                        st.divider()
                        shares_count = int(investment // current_price)
                        actual_invested = shares_count * current_price
                        expected_profit = (target_a - current_price) * shares_count
                        
                        st.markdown("### 💰 Investment Plan")
                        st.success(f"Capital: **₹{investment:.2f}** | Shares to Buy: **{shares_count}** | Amount Used: **₹{actual_invested:.2f}** | Expected Profit (At T1): **₹{expected_profit:.2f}**")

            except Exception as e:
                st.error(f"Software me ek choti error aayi hai: {e}")

st.caption("Disclaimer: Yeh tool sirf sikhne (educational purposes) ke liye hai. Market mein risk hota hai, kripya apni research zaroor karein.")
