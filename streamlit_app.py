import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pytz # Tambahkan ini di requirements.txt untuk zona waktu WIB

# Setup Halaman
st.set_page_config(page_title="IDX PROP DESK", layout="wide")

# Fungsi Ambil Data
@st.cache_data(ttl=300)
def get_data():
    # 1. Tickers list (Level 1 indentation - 4 spaces)
    tickers = ["AADI.JK", "AALI.JK", "ABBA.JK", "ABDA.JK", "ABMM.JK", "ACES.JK"] # ... add the rest
    data_list = []
    
    # 2. The Loop (Level 1 indentation - must match 'data_list')
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            df_hist = stock.history(period="5d")
            
            if df_hist.empty or len(df_hist) < 2: 
                continue
            
            # 3. Calculations (Level 2 indentation - 8 spaces)
            last_close = df_hist['Close'].iloc[-1]
            prev_close = df_hist['Close'].iloc[-2]
            change = ((last_close - prev_close) / prev_close) * 100
            
            atr_val = (df_hist['High'] - df_hist['Low']).mean()
            atr_pct = (atr_val / last_close) * 100
            
            avg_volume_5d = df_hist['Volume'].mean()
            current_volume = df_hist['Volume'].iloc[-1]
            
            grade = "No Grade"
            if change > 3.0 and atr_pct > 3.0 and current_volume > (1.5 * avg_volume_5d):
                grade = "Grade A"
            elif change > 1.5 and atr_pct > 2.0:
                grade = "Grade B"

            data_list.append({
                "Symbol": t.replace(".JK", ""),
                "Price": int(last_close),
                "Change %": round(change, 2),
                "ATR %": round(atr_pct, 2),
                "Grade": grade
            })
        except Exception:
            continue
            
    return pd.DataFrame(data_list)

# Tampilan Header
st.title("📈 IDX Live Stock Screener")
# 2. Pengaturan Zona Waktu (WIB)
wib = pytz.timezone('Asia/Jakarta')
waktu_sekarang = datetime.now(wib).strftime('%H:%M:%S')

# 3. Tampilan Header Live (Sesuai Gambar Utama)
col_head1, col_head2 = st.columns([3, 1])

with col_head1:
    # Menampilkan indikator titik hijau dan waktu live
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="color: #28a745; font-size: 20px;">●</span>
            <span style="font-weight: bold;">IDX Market LIVE</span>
            <span style="color: #666;">| Last updated: {waktu_sekarang} WIB</span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.caption("Auto-refreshing screener for IDX stocks with real-time data.")

# Layout untuk bagian refresh rate (di atas tabel)
col_refresh_info, col_spacer, col_countdown = st.columns([3, 1, 1])

with col_refresh_info:
    # Menampilkan teks "Refresh rate 15 seconds" dengan ikon reload
    st.markdown("🔄 Refresh rate 15 seconds")

with col_countdown:
    # Menampilkan "Refresh in: 12s" di pojok kanan atas tabel
    # Catatan: Angka detik ini akan reset setiap kali halaman refresh otomatis
    st.markdown(
        f"""
        <div style="text-align: right; color: #666; font-size: 14px;">
            <span style="font-size: 18px;">↻</span> Refresh in: <span style="color: #e74c3c;">15s</span> >
        </div>
        """, 
        unsafe_allow_html=True
    )
	
# Load Data
df = get_data()

if not df.empty:

    # Metric Grade A

    grade_a = len(df[df['Grade'] == "Grade A"])

    st.metric("Grade A Signals:", grade_a)
	
	# Tabel Data
    st.dataframe(df, use_container_width=True, hide_index=True)
    # Chart ATR
    st.subheader("ATR Percent Ranking")
    fig = px.bar(df, x='Symbol', y='ATR %', color='ATR %', color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Gagal mengambil data dari Yahoo Finance. Coba refresh halaman.")

from streamlit_option_menu import option_menu
	
# 2. Sidebar Navigation
with st.sidebar:
    st.markdown("### 🔴 **Streamlit**")
    st.write("")
    
    # Membuat Menu Navigasi Bergaya Pro
    selected = option_menu(
        menu_title=None,  # Tidak pakai judul menu
        options=["Live Screener", "Grade A Signals", "Risk Settings", "Execution Tickets"],
        icons=["globe", "graph-up-arrow", "gear", "file-text"], # Nama ikon bootstrap
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#f0f2f6"},
            "icon": {"color": "#444", "font-size": "18px"}, 
            "nav-link": {
                "font-size": "16px", 
                "text-align": "left", 
                "margin": "0px", 
                "--hover-color": "#eee"
            },
            "nav-link-selected": {"background-color": "#4e8df5"}, # Warna biru saat terpilih
        }
    )
    
    st.write("---")
    st.caption("Prop Desk v1.0")

# Logika untuk menampilkan konten berdasarkan menu yang dipilih
if selected == "Live Screener":
    # Masukkan kode tabel screener Anda di sini
    st.subheader("🌐 IDX Live Stock Screener")
    # ... (kode fungsi data dan tabel)
    
elif selected == "Grade A Signals":
    st.subheader("📈 Grade A Signals")
    st.write("Daftar sinyal trading aktif akan muncul di sini.")

elif selected == "Risk Settings":
    st.title("⚙️ Risk Settings")
    st.write("Konfigurasi parameter risiko trading untuk membatasi eksposur portofolio Anda.")
    
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Trading Parameters")
        risk_per_trade = st.number_input("Max Risk per Trade (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
        max_position = st.slider("Max Open Positions", 1, 20, 5)
        st.caption("Menentukan berapa persen modal yang siap hilang dalam satu posisi.")

    with col2:
        st.subheader("Stop Loss & Take Profit")
        default_sl = st.number_input("Default Stop Loss (%)", min_value=0.5, max_value=20.0, value=5.0)
        default_tp = st.number_input("Default Take Profit (%)", min_value=1.0, max_value=50.0, value=15.0)
    
    st.write("---")
    
    # Fitur tambahan: Kalkulator Posisi Sederhana
    st.subheader("Position Sizing Calculator")
    capital = st.number_input("Total Trading Capital (IDR)", min_value=1000000, value=10000000, step=1000000)
    
    if st.button("Save & Apply Settings"):
        # Menyimpan nilai ke session state agar bisa dipakai di menu Screener
        st.session_state['risk_pct'] = risk_per_trade
        st.session_state['sl_pct'] = default_sl
        
        # Hitung risiko nominal
        risk_amount = capital * (risk_per_trade / 100)
        st.success(f"Settings Saved! Maksimal risiko per trade Anda adalah: Rp {risk_amount:,.0f}")

elif selected == "Execution Tickets":
    st.subheader("📄 Execution Tickets")
    st.write("Silakan upload daftar saham dalam format Excel (.xlsx) dari IDX untuk diproses.")
    
    # Komponen Drag and Drop sesuai Screenshot 18
    uploaded_file = st.file_uploader(
        "Drag and drop file here", 
        type=["xlsx"], 
        help="Limit 200MB per file • XLSX"
    )

    if uploaded_file is not None:
        try:
            # Membaca file excel
            df_excel = pd.read_excel(uploaded_file)
            st.success("File berhasil diupload!")
            
            # Menampilkan pratinjau data yang diupload
            st.write("### Preview Daftar Saham")
            st.dataframe(df_excel, use_container_width=True)
            
            # Contoh tombol untuk memproses data tersebut ke screener
            if st.button("Proses ke Screener"):
                st.info("Memproses data saham dari Excel...")
                # Di sini Anda bisa menambahkan logika untuk mengambil kolom Simbol/Ticker 
                # dan memasukkannya ke fungsi get_data()
                
        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca file: {e}")
    st.info("Parameter ini akan digunakan secara otomatis untuk menghitung 'Edge' dan 'Risk Reward Ratio' pada tabel Live Screener.")
	
from streamlit_autorefresh import st_autorefresh

# Menyetel refresh otomatis setiap 15 detik
# key="datarefresh" digunakan agar Streamlit bisa melacak widget ini
count = st_autorefresh(interval=15000, key="datarefresh")
