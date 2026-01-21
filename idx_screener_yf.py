import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime, timedelta

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="IDX Prop Desk Screener", layout="wide")

# Custom CSS untuk tampilan gelap/profesional
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 40px; color: #2ecc71; }
    .stDataFrame { border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI DATA ---
@st.cache_data(ttl=60) # Cache data selama 60 detik agar tidak terkena ban yfinance
def fetch_idx_data(tickers):
    results = []
    for t in tickers:
        try:
            # Ambil data historis untuk menghitung ATR (14 hari terakhir)
            stock = yf.Ticker(f"{t}.JK")
            hist = stock.history(period="1mo")
            
            if len(hist) < 2: continue

            # Ambil harga terakhir & harga sebelumnya
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            # Hitung Simple ATR (High - Low) as percentage of price
            recent_volatility = (hist['High'] - hist['Low']).rolling(window=14).mean().iloc[-1]
            atr_pct = (recent_volatility / current_price) * 100
            
            # Simulasi Volume dalam Jutaan
            vol_m = hist['Volume'].iloc[-1] / 1_000_000
            
            # Logika Penentuan Grade (Simulasi)
            edge = (change_pct * 0.7) + (atr_pct * 0.3)
            grade = "No Grade"
            if change_pct > 1.0 and atr_pct > 1.5: grade = "Grade A"
            elif change_pct > 0.5: grade = "Grade B"
            elif change_pct > 0: grade = "Grade C"

            results.append({
                "Symbol": t,
                "Price": round(current_price, 0),
                "Change %": round(change_pct, 2),
                "Vol (M)": f"{vol_m:.1f}M",
                "ATR %": round(atr_pct, 2),
                "Grade": grade,
                "Edge": round(edge, 2)
            })
        except:
            continue
    return pd.DataFrame(results)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔴 Streamlit")
    st.radio("Menu", ["Live Screener", "Grade A Signals", "Risk Settings"])
    st.divider()
    refresh_rate = st.slider("Refresh rate (sec)", 15, 60, 30)

# --- HEADER ---
watch_list = ["BBCA", "BBRI", "BMRI", "TLKM", "ASII", "MDKA", "BUKA", "GOTO", "ADRO"]
df = fetch_idx_data(watch_list)

col1, col2 = st.columns([3, 1])
with col1:
    st.title("IDXX LIVE STOCK SCREENER")
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')} WIB")

with col2:
    grade_a_count = len(df[df['Grade'] == "Grade A"])
    st.metric("Grade A Signals", grade_a_count)

# --- TABEL SCREENER ---
# Styling warna untuk kolom Change %
def color_change(val):
    color = '#2ecc71' if val > 0 else '#e74c3c'
    return f'color: {color}'

st.dataframe(
    df.style.applymap(color_change, subset=['Change %']),
    use_container_width=True,
    hide_index=True
)

# --- ATR RANKING CHART ---
st.subheader("ATR Percent Ranking")
# Filter data untuk chart
df_sorted = df.sort_values('ATR %', ascending=False)

fig = px.bar(
    df_sorted, 
    x='Symbol', 
    y='ATR %', 
    text='ATR %',
    color='ATR %',
    color_continuous_scale='RdYlGn_r', # Merah untuk ATR tinggi (risiko)
    template="plotly_dark"
)

fig.update_layout(
    xaxis_title="",
    yaxis_title="ATR Percentage",
    height=400,
    margin=dict(l=20, r=20, t=20, b=20)
)
st.plotly_chart(fig, use_container_width=True)

# --- AUTO REFRESH ---
# Catatan: st.rerun() akan menyebabkan refresh seluruh halaman
# st.empty()
# time.sleep(refresh_rate)
# st.rerun()
