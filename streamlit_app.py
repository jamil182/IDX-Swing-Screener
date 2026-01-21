import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

# Setup Halaman
st.set_page_config(page_title="IDX PROP DESK", layout="wide")

# Fungsi Ambil Data
@st.cache_data(ttl=300)
def get_data():
    # Daftar saham IDX
    tickers = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "MDKA.JK", "BUKA.JK", "GOTO.JK"]
    data_list = []
    
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            # Ambil data 5 hari terakhir
            df_hist = stock.history(period="5d")
            if df_hist.empty: continue
            
            last_close = df_hist['Close'].iloc[-1]
            prev_close = df_hist['Close'].iloc[-2]
            change = ((last_close - prev_close) / prev_close) * 100
            
            # Perhitungan ATR Sederhana
            atr_val = (df_hist['High'] - df_hist['Low']).mean()
            atr_pct = (atr_val / last_close) * 100
            
            # Penentuan Grade
            grade = "No Grade"
            if change > 1.0 and atr_pct > 1.5: grade = "Grade A"
            elif change > 0.5: grade = "Grade B"

            data_list.append({
                "Symbol": t.replace(".JK", ""),
                "Price": int(last_close),
                "Change %": round(change, 2),
                "ATR %": round(atr_pct, 2),
                "Grade": grade
            })
        except:
            continue
    return pd.DataFrame(data_list)

# Tampilan Header
st.title("📈 IDX Live Stock Screener")
st.write(f"Update Terakhir: {datetime.now().strftime('%H:%M:%S')} WIB")

# Load Data
df = get_data()

if not df.empty:
    # Metric Grade A
    grade_a = len(df[df['Grade'] == "Grade A"])
    st.metric("Grade A Signals", grade_a)

    # Tabel Data
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Chart ATR
    st.subheader("ATR Percent Ranking")
    fig = px.bar(df, x='Symbol', y='ATR %', color='ATR %', color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Gagal mengambil data dari Yahoo Finance. Coba refresh halaman.")
