import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Pro Stock Technical Analyzer", page_icon="📈", layout="centered")

st.title("📈 Pro Stock Technical Analyzer")
st.markdown("Advanced Technical Analysis, Market Scanner, Buy/Sell Signals & Beginner Guide.")

# --- SCANNER SECTION ---
st.markdown("### 🔍 Smart Market Scanner")
if st.button("🚀 Find Trending Stocks", use_container_width=True):
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
    my_bar = st.progress(0, text="Market scan shuru ho raha hai...")
    
    for i, stock in enumerate(scan_list):
        my_bar.progress((i + 1) / len(scan_list), text=f"Scanning {stock.replace('.NS', '')}...")
        try:
            df_scan = yf.download(stock, period="6mo", progress=False)
            if df_scan.empty: continue
            if isinstance(df_scan.columns, pd.MultiIndex):
                df_scan.columns = df_scan.columns.get_level_values(0)
            
            close_scan = df_scan['Close']
            c_price = float(close_scan.iloc[-1])
            dma20 = float(close_scan.rolling(20).mean().iloc[-1])
            
            delta = close_scan.diff()
            gain = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
            loss = (-1 * delta.clip(upper=0)).ewm(com=13, adjust=False).mean()
            rs = gain / loss
            rsi = float((100 - (100 / (1 + rs))).iloc[-1])
            
            ema12 = close_scan.ewm(span=12, adjust=False).mean()
            ema26 = close_scan.ewm(span=26, adjust=False).mean()
            macd = ema12 - ema26
            macd_sig = macd.ewm(span=9, adjust=False).mean()
            
            if (c_price > dma20) and (float(macd.iloc[-1]) > float(macd_sig.iloc[-1])) and (40 <= rsi <= 70):
                trending_stocks.append({"Symbol": stock.replace(".NS", ""), "Price (₹)": round(c_price, 2), "RSI": round(rsi, 1), "Trend": "Bullish 🟢"})
        except:
            pass
            
    my_bar.empty()
    if trending_stocks:
        st.success(f"🎉 {len(trending_stocks)} Trending Stocks mile hain.")
        st.dataframe(pd.DataFrame(trending_stocks).set_index("Symbol"), use_container_width=True)
        st.info("💡 **PRO TIP:** Symbol copy karein aur niche paste karke poora analysis dekhein!")
    else:
        st.warning("🔴 Koi clear buy signal nahi mila.")

st.divider()

# --- MAIN ANALYZER SECTION ---
st.markdown("### 🔍 Full Stock Analysis")
trading_style = st.selectbox("Trading Style Select Karein:", ["Swing (Weeks to Months)", "Intraday (Same Day) & BTST", "Long Term (1-5 Years)"])

c1, c2 = st.columns(2)
with c1: exchange = st.selectbox("Exchange", ["NSE", "BSE"])
with c2: raw_symbol = st.text_input("Stock Symbol (e.g., ZOMATO)", value="").strip().upper()

c3, c4 = st.columns(2)
with c3: investment = st.number_input("New Investment (₹) [Optional]", min_value=0.0, step=1000.0)
with c4: purchase_price = st.number_input("Buy Price (₹) [Optional]", min_value=0.0, step=10.0)

if st.button("📊 Analyze This Stock", use_container_width=True):
    if not raw_symbol:
        st.error("Kripya Stock Symbol dalein!")
    else:
        symbol = raw_symbol
        if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
            symbol += ".NS" if exchange == "NSE" else ".BO"

        if trading_style == "Intraday (Same Day) & BTST":
            dl_period, dl_interval, ma1, ma2, ma3 = "5d", "15m", 9, 21, 50
            t1, t2, t3, sl_pct, tf_label, supp_window, hl_label = 1.01, 1.02, 1.03, 0.99, "15-Min", 20, "5-Day"
        elif trading_style == "Long Term (1-5 Years)":
            dl_period, dl_interval, ma1, ma2, ma3 = "5y", "1wk", 20, 50, 200
            t1, t2, t3, sl_pct, tf_label, supp_window, hl_label = 1.50, 2.00, 3.00, 0.85, "Weekly", 52, "5-Year"
        else:
            dl_period, dl_interval, ma1, ma2, ma3 = "1y", "1d", 20, 50, 200
            t1, t2, t3, sl_pct, tf_label, supp_window, hl_label = 1.10, 1.15, 1.20, 0.95, "Daily", 30, "52-Week"

        with st.spinner(f"Fetching {tf_label} data for {symbol}..."):
            try:
                df = yf.download(symbol, period=dl_period, interval=dl_interval, progress=False)
                if df.empty:
                    st.error("❌ Data nahi mila. Symbol ya Exchange check karein.")
                else:
                    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                    
                    close = df['Close']
                    c_price = float(close.iloc[-1])
                    
                    sma1 = float(close.rolling(ma1).mean().iloc[-1]) if len(close) >= ma1 else c_price
                    sma2 = float(close.rolling(ma2).mean().iloc[-1]) if len(close) >= ma2 else c_price
                    sma3 = float(close.rolling(ma3).mean().iloc[-1]) if len(close) >= ma3 else c_price
                    ema1 = float(close.ewm(span=ma1, adjust=False).mean().iloc[-1])
                    ema2 = float(close.ewm(span=ma2, adjust=False).mean().iloc[-1])

                    delta = close.diff()
                    gain = delta.clip(lower=0).ewm(com=13, adjust=False).mean().iloc[-1]
                    loss = (-1 * delta.clip(upper=0)).ewm(com=13, adjust=False).mean().iloc[-1]
                    rsi = float(100 - (100 / (1 + (gain/loss)))) if loss != 0 else 100
                    rsi_status = "Overbought 🔴" if rsi > 70 else "Oversold 🟢" if rsi < 30 else "Neutral 🟡"

                    ema12 = close.ewm(span=12, adjust=False).mean()
                    ema26 = close.ewm(span=26, adjust=False).mean()
                    macd = ema12 - ema26
                    macd_sig = macd.ewm(span=9, adjust=False).mean()
                    is_macd_bullish = float(macd.iloc[-1]) > float(macd_sig.iloc[-1])

                    recent_data = df.tail(supp_window)
                    support, resistance = float(recent_data['Low'].min()), float(recent_data['High'].max())
                    
                    avg_vol = float(df['Volume'].rolling(ma1).mean().iloc[-1]) if len(df['Volume']) >= ma1 else 1.0
                    vol_ratio = float(df['Volume'].iloc[-1] / avg_vol) if avg_vol > 0 else 1.0
                    
                    std_20 = float(close.rolling(20).std().iloc[-1]) if len(close) >= 20 else 0
                    bb_middle = float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else c_price
                    bb_upper, bb_lower = bb_middle + (2 * std_20), bb_middle - (2 * std_20)

                    p_high, p_low = float(df['High'].max()), float(df['Low'].min())
                    
                    buy_zone, strong_buy, stop_loss = c_price * 0.99, support if support < c_price else c_price * sl_pct, support * 0.99
                    ta, tb, tc = c_price * t1, c_price * t2, c_price * t3

                    if c_price > sma2 and sma2 > sma3: trend_status, trend_reason = "UPTREND 📈", f"Price {ma2} SMA ke upar hai."
                    elif c_price < sma2 and sma2 < sma3: trend_status, trend_reason = "DOWNTREND 📉", f"Price {ma2} & {ma3} SMA ke niche hai."
                    else: trend_status, trend_reason = "SIDEWAYS ↔️", "Price range bound hai."

                    if "UPTREND" in trend_status and (ema1 > ema2) and is_macd_bullish and (40 <= rsi <= 70):
                        s_box, s_title, s_msg = st.success, "🟢 FRESH BUY", f"{trend_reason} EMA & MACD Bullish hain."
                    elif rsi < 35 or c_price <= bb_lower:
                        s_box, s_title, s_msg = st.info, "🟡 ACCUMULATE (Oversold)", "Stock lower band ya support par hai."
                    elif c_price >= bb_upper or rsi > 70:
                        s_box, s_title, s_msg = st.warning, "🔴 WAIT (Overbought)", "Stock Overbought hai, dip ka wait karein."
                    else:
                        s_box, s_title, s_msg = st.error, "🔴 NO SIGNAL", "Abhi clear buy signal nahi hai."

                    st.subheader(f"Results for {symbol} ({trading_style})")
                    if purchase_price == 0: s_box(f"**{s_title}**\n\n{s_msg}")
                    else:
                        pnl_pct = ((c_price - purchase_price) / purchase_price) * 100
                        st.markdown("### 💼 Portfolio Status")
                        if pnl_pct > 0: st.success(f"**Profit:** ₹{c_price - purchase_price:.2f} (+{pnl_pct:.2f}%)")
                        else: st.error(f"**Loss:** ₹{abs(c_price - purchase_price):.2f} ({pnl_pct:.2f}%)")

                    st.divider()
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Price", f"₹{c_price:.2f}")
                    m2.metric("Trend", trend_status.split()[0])
                    m3.metric("RSI (14)", f"{rsi:.1f}")
                    m4.metric("Vol vs Avg", f"{vol_ratio:.1f}x")
                    st.divider()

                    cl, cr = st.columns(2)
                    with cl:
                        st.markdown(f"### 📊 Action Zones ({tf_label})")
                        st.write(f"**Buy Zone:** ₹{buy_zone:.2f} - ₹{c_price:.2f}\n**Strong Buy:** ₹{strong_buy:.2f}\n**Stop-Loss:** ₹{stop_loss:.2f}")
                        with st.expander("💡 Iska kya matlab hai?"): st.info("Buy Zone safe buying range hai. Strong buy sasta level hai. Stop-Loss par nuksan rokne ke liye exit kar lein.")
                        
                        st.markdown("### 🎯 Targets")
                        st.write(f"**T1:** ₹{ta:.2f} | **T2:** ₹{tb:.2f} | **T3:** ₹{tc:.2f}")
                        with st.expander("💡 Target ka matlab?"): st.info("Kharidne ke baad in levels par aane par aap apna profit book (sell) kar sakte hain.")
                        
                        st.markdown(f"### 🏆 {hl_label} Range")
                        st.write(f"**High:** ₹{p_high:.2f} | **Low:** ₹{p_low:.2f}")
                        with st.expander("💡 Range ka matlab?"): st.info("Yeh batata hai ki stock apne pichle highest price se abhi kitna sasta (discounted) mil raha hai.")
                    
                    with cr:
                        st.markdown("### 📉 Technicals")
                        st.write(f"**RSI:** {rsi:.1f} ({rsi_status})\n**MACD:** {'Bullish 🟢' if is_macd_bullish else 'Bearish 🔴'}\n**Support:** ₹{support:.2f} | **Resistance:** ₹{resistance:.2f}")
                        with st.expander("💡 Technicals kya batate hain?"): st.info(f"**RSI:** 70+ (Mahenga/Overbought), 30- (Sasta/Oversold).\n**MACD:** {'Buying momentum hai 🟢' if is_macd_bullish else 'Selling pressure hai 🔴'}\n**Support:** Girne se rokne wala level.\n**Resistance:** Upar jane se rokne wala level.")
                        
                        st.markdown("### 📈 Averages")
                        st.write(f"**{ma1} EMA:** ₹{ema1:.2f} | **{ma2} EMA:** ₹{ema2:.2f}\n**{ma3} SMA:** ₹{sma3:.2f}")
                        with st.expander("💡 Averages ka kya kaam hai?"): st.info(f"Is mode me automatically {ma1}, {ma2}, aur {ma3} period use ho raha hai. Price inke upar ho toh trend strong hota hai.")
                        
                        st.markdown("### 🌀 Bollinger Bands")
                        st.write(f"**Upper:** ₹{bb_upper:.2f} | **Lower:** ₹{bb_lower:.2f}")
                        with st.expander("💡 Bollinger Bands ka matlab?"): st.info("**Lower Band:** Price iske paas ho toh sasta (Oversold) hai.\n**Upper Band:** Price iske paas ho toh mahenga (Overbought) hai.")

                    if investment > 0 and purchase_price == 0:
                        shares = int(investment // c_price)
                        st.success(f"**Investment Plan:** Capital: ₹{investment:.2f} | Shares: {shares} | Used: ₹{shares * c_price:.2f} | Exp. Profit (T1): ₹{(ta - c_price) * shares:.2f}")

            except Exception as e:
                st.error(f"Error aayi: {e}")

st.caption("Disclaimer: Yeh tool sirf sikhne (educational purposes) ke liye hai.")
