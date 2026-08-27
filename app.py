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
            
            # ✨ NaN Fix: Data Cleaner
            df_scan.dropna(subset=['Close', 'High', 'Low'], inplace=True)
            if df_scan.empty: continue
            
            close_scan = df_scan['Close']
            current_price = float(close_scan.iloc[-1])
            
            dma20_val = close_scan.rolling(20).mean().iloc[-1]
            if pd.isna(dma20_val): continue
            dma20 = float(dma20_val)
            
            delta = close_scan.diff()
            gain = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
            loss = (-1 * delta.clip(upper=0)).ewm(com=13, adjust=False).mean()
            rs = gain / loss
            rsi = float((100 - (100 / (1 + rs))).iloc[-1])
            
            ema12 = close_scan.ewm(span=12, adjust=False).mean()
            ema26 = close_scan.ewm(span=26, adjust=False).mean()
            macd = ema12 - ema26
            macd_sig = macd.ewm(span=9, adjust=False).mean()
            
            if (current_price > dma20) and (float(macd.iloc[-1]) > float(macd_sig.iloc[-1])) and (35 <= rsi <= 75):
                trending_stocks.append({"Symbol": stock.replace(".NS", ""), "Price (₹)": round(current_price, 2), "RSI": round(rsi, 1), "Trend": "Bullish 🟢"})
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
                    if isinstance(df.columns, pd.MultiIndex): 
                        df.columns = df.columns.get_level_values(0)
                    
                    # ✨ NaN Fix: Sabse zaroori line jo blank data hatayegi
                    df.dropna(subset=['Close', 'High', 'Low'], inplace=True)
                    
                    if df.empty:
                        st.error("❌ Stock ka complete data nahi mil raha (Trading band ho sakti hai).")
                    else:
                        close = df['Close']
                        current_price = float(close.iloc[-1])
                        
                        # Averages with NaN safety for new stocks
                        sma1_val = close.rolling(ma1).mean().iloc[-1]
                        sma1 = float(sma1_val) if not pd.isna(sma1_val) else current_price
                        
                        sma2_val = close.rolling(ma2).mean().iloc[-1]
                        sma2 = float(sma2_val) if not pd.isna(sma2_val) else current_price
                        
                        sma3_val = close.rolling(ma3).mean().iloc[-1]
                        sma3 = float(sma3_val) if not pd.isna(sma3_val) else current_price
                        
                        ema1 = float(close.ewm(span=ma1, adjust=False).mean().iloc[-1])
                        ema2 = float(close.ewm(span=ma2, adjust=False).mean().iloc[-1])

                        if trading_style == "Intraday (Same Day) & BTST":
                            df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
                            df['TP_Volume'] = df['Typical_Price'] * df['Volume']
                            df['Cumulative_Volume'] = df.groupby(df.index.date)['Volume'].cumsum()
                            df['Cumulative_TP_Volume'] = df.groupby(df.index.date)['TP_Volume'].cumsum()
                            df['VWAP'] = df['Cumulative_TP_Volume'] / df['Cumulative_Volume']
                            vwap_price = float(df['VWAP'].iloc[-1])

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
                        support = float(recent_data['Low'].min())
                        resistance = float(recent_data['High'].max())
                        
                        avg_vol_val = df['Volume'].rolling(ma1).mean().iloc[-1]
                        avg_vol = float(avg_vol_val) if not pd.isna(avg_vol_val) and avg_vol_val > 0 else 1.0
                        vol_ratio = float(df['Volume'].iloc[-1] / avg_vol)
                        
                        # Bollinger Bands with NaN safety
                        std_20_val = close.rolling(20).std().iloc[-1]
                        std_20 = float(std_20_val) if not pd.isna(std_20_val) else 0.0
                        
                        bb_middle_val = close.rolling(20).mean().iloc[-1]
                        bb_middle = float(bb_middle_val) if not pd.isna(bb_middle_val) else current_price
                        
                        bb_upper = bb_middle + (2 * std_20)
                        bb_lower = bb_middle - (2 * std_20)

                        p_high, p_low = float(df['High'].max()), float(df['Low'].min())
                        
                        buy_zone = current_price * 0.99
                        strong_buy = support if support < current_price else current_price * sl_pct
                        stop_loss = support * 0.99
                        
                        ta, tb, tc = current_price * t1, current_price * t2, current_price * t3

                        if current_price > sma2 and sma2 > sma3: 
                            trend_status, trend_reason = "UPTREND 📈", f"Price {ma2} SMA ke upar hai."
                        elif current_price < sma2 and sma2 < sma3: 
                            trend_status, trend_reason = "DOWNTREND 📉", f"Price {ma2} & {ma3} SMA ke niche hai."
                        else: 
                            trend_status, trend_reason = "SIDEWAYS ↔️", "Price range bound hai."

                        if "UPTREND" in trend_status and (ema1 > ema2) and is_macd_bullish and (40 <= rsi <= 70):
                            s_box, s_title, s_msg = st.success, "🟢 FRESH BUY", f"{trend_reason} EMA & MACD Bullish hain."
                        elif rsi < 35 or current_price <= bb_lower:
                            s_box, s_title, s_msg = st.info, "🟡 ACCUMULATE (Oversold)", "Stock lower band ya support par hai."
                        elif current_price >= bb_upper or rsi > 70:
                            s_box, s_title, s_msg = st.warning, "🔴 WAIT (Overbought)", "Stock Overbought hai, dip ka wait karein."
                        else:
                            s_box, s_title, s_msg = st.error, "🔴 NO SIGNAL", "Abhi clear buy signal nahi hai."

                        st.subheader(f"Results for {symbol} ({trading_style})")
                        if purchase_price == 0: 
                            s_box(f"**{s_title}**\n\n{s_msg}")
                        else:
                            pnl_pct = ((current_price - purchase_price) / purchase_price) * 100
                            pnl_amt = current_price - purchase_price
                            st.markdown("### 💼 Portfolio Status")
                            if pnl_pct > 0: 
                                st.success(f"**Profit:** ₹{pnl_amt:.2f} per share (+{pnl_pct:.2f}%)")
                            else: 
                                st.error(f"**Loss:** ₹{abs(pnl_amt):.2f} per share ({pnl_pct:.2f}%)")

                        st.divider()
                        
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Current Price", f"₹{current_price:.2f}")
                        m2.metric("Trend", trend_status.split()[0])
                        m3.metric("RSI (14)", f"{rsi:.1f}")
                        m4.metric("Vol Vs Avg", f"{vol_ratio:.1f}x")
                        
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
                            st.write(f"**T1:** ₹{ta:.2f} | **T2:** ₹{tb:.2f} | **T3:** ₹{tc:.2f}")
                            with st.expander("💡 Target ka matlab?"): 
                                st.info("Kharidne ke baad in levels par price aane par aap apna thoda-thoda profit book (sell) kar sakte hain.")
                            
                            st.markdown(f"### 🏆 {hl_label} Range")
                            st.write(f"**High:** ₹{p_high:.2f} | **Low:** ₹{p_low:.2f}")
                            with st.expander("💡 Range ka matlab?"): 
                                st.info("Yeh batata hai ki stock apne pichle highest price se abhi kitna sasta (discounted) mil raha hai.")
                        
                        with col_right:
                            st.markdown("### 📉 Technicals")
                            st.write(f"**RSI (14):** {rsi:.1f} ({rsi_status})")
                            st.write(f"**MACD:** {'Bullish 🟢' if is_macd_bullish else 'Bearish 🔴'}")
                            st.write(f"**Support:** ₹{support:.2f} | **Resistance:** ₹{resistance:.2f}")
                            with st.expander("💡 Technicals kya batate hain?"): 
                                st.info(f"**RSI:** 70 se upar (Mahenga/Overbought), 30 se niche (Sasta/Oversold).\n**MACD:** {'Buying momentum hai 🟢' if is_macd_bullish else 'Selling pressure chal rahi hai 🔴'}.\n**Support:** Jaha se price niche girna band karta hai.\n**Resistance:** Jaha se price upar jane mein rukta hai.")
                            
                            st.markdown("### 📈 Moving Averages")
                            st.write(f"**{ma1} EMA:** ₹{ema1:.2f} | **{ma2} EMA:** ₹{ema2:.2f}")
                            st.write(f"**{ma3} SMA:** ₹{sma3:.2f}")
                            
                            if trading_style == "Intraday (Same Day) & BTST":
                                vwap_trend = "Bullish 🟢" if current_price > vwap_price else "Bearish 🔴"
                                st.write(f"**VWAP (Today):** ₹{vwap_price:.2f} ({vwap_trend})")
                            
                            with st.expander("💡 Averages ka kya kaam hai?"): 
                                vwap_desc = "\n\n**VWAP:** Intraday (Day trading) ka sabse bada indicator. Agar current price VWAP ke UPAR hai, toh stock tezi (Bullish) mein hota hai." if trading_style == "Intraday (Same Day) & BTST" else ""
                                st.info(f"Is mode mein system automatically {ma1}, {ma2}, aur {ma3} period ke averages use kar raha hai. Current price agar Averages ke UPAR ho, toh stock ko strong Uptrend mein maana jata hai.{vwap_desc}")
                            
                            st.markdown("### 🌀 Bollinger Bands")
                            st.write(f"**Upper Band:** ₹{bb_upper:.2f} | **Lower Band:** ₹{bb_lower:.2f}")
                            with st.expander("💡 Bollinger Bands ka matlab?"): 
                                st.info("**Lower Band:** Jab price iske paas ho toh stock bahut sasta (Oversold) hota hai.\n**Upper Band:** Jab price iske paas ho toh stock mahenga (Overbought) hota hai.")

                        if investment > 0 and purchase_price == 0:
                            st.divider()
                            shares_count = int(investment // current_price)
                            st.success(f"**Investment Plan:** Capital: **₹{investment:.2f}** | Shares to Buy: **{shares_count}** | Amount Used: **₹{shares_count * current_price:.2f}** | Expected Profit (At T1): **₹{(ta - current_price) * shares_count:.2f}**")

            except Exception as e:
                st.error(f"Software me ek choti error aayi hai: {e}")

st.caption("Disclaimer: Yeh tool sirf sikhne (Educational Purposes) ke liye hai. Investment se pehle apni research zaroor karein (Do your own research before investing).")
