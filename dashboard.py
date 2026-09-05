import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="FIRELINE: Data Findings", layout="wide", page_icon="🔥", initial_sidebar_state="collapsed")

# Styling
st.markdown("""
<style>
    .header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 5px; }
    .subheader { font-size: 1.2rem; font-weight: 400; color: #4B5563; margin-bottom: 25px; }
    .section-title { font-size: 1.5rem; font-weight: 700; color: #111827; margin-top: 30px; margin-bottom: 10px; border-bottom: 2px solid #E5E7EB; padding-bottom: 5px; }
    .answer-box { padding: 15px; border-radius: 5px; background-color: #EFF6FF; border-left: 5px solid #3B82F6; color: #1E3A8A; margin-bottom: 20px;}
    .alert-box { padding: 15px; border-radius: 5px; background-color: #FEF2F2; border-left: 5px solid #EF4444; color: #991B1B; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">🔥 FIRELINE: Analisis Data Eksploratif & Prioritisasi</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Menjawab Krisis Waktu dan Fragmentasi Informasi dalam Penanganan Karhutla Kalimantan.</div>', unsafe_allow_html=True)

st.markdown("""
**Masalah Sesungguhnya:** Setiap musim kemarau, satelit menangkap **puluhan ribu titik panas**. Petugas lapangan bekerja tanpa panduan prioritas yang jelas karena *fragmentasi informasi* (data satelit, lokasi populasi, dan cuaca terpisah). Akibatnya, verifikasi lapangan memakan waktu **12-24 jam**.  
**Misi FIRELINE:** Menyatukan data tersebut untuk menjawab 4 pertanyaan operasional secara instan.
""")

# Load Data
@st.cache_data
def load_data():
    file_path = os.path.join("data", "processed", "hotspot_scored_final.csv")
    if not os.path.exists(file_path):
        return pd.DataFrame()
    df = pd.read_csv(file_path)
    if 'date_local' in df.columns:
        df['date_local'] = pd.to_datetime(df['date_local'])
        df['year'] = df['date_local'].dt.year
        df['month'] = df['date_local'].dt.month
    return df

df = load_data()

# Helper for images
def show_image(filename, caption=""):
    img_path = os.path.join("outputs", "figures", filename)
    if os.path.exists(img_path):
        st.image(img_path, caption=caption, use_container_width=True)
    else:
        st.warning(f"Gambar {filename} tidak ditemukan di outputs/figures/")

st.markdown('<div class="section-title">Pertanyaan 1: Mengapa Kita Butuh Sistem Prioritas (Bukan Sekadar Reaktif)?</div>', unsafe_allow_html=True)
st.markdown("Kemunculan titik api sangat dinamis dan masif. Kita tidak bisa merespons semuanya secara bersamaan.")
c1, c2 = st.columns(2)
with c1:
    show_image("A1_tren_harian.png", "Tren harian menunjukkan lonjakan titik api yang tiba-tiba, menyulitkan respons reaktif.")
with c2:
    show_image("A4_perbandingan_tahunan.png", "Perbandingan tahunan (Peringatan: Tahun 2026 merupakan data parsial).")

st.markdown('<div class="section-title">Pertanyaan 2: Siapa Populasi yang Paling Rentan Terpapar?</div>', unsafe_allow_html=True)
st.markdown("Tidak semua titik api sama berbahayanya. Api yang berdekatan dengan fasilitas penduduk jauh lebih mengancam.")
c3, c4 = st.columns(2)
with c3:
    show_image("B1_jumlah_provinsi.png", "Sebaran jumlah deteksi per provinsi. Kalimantan Barat merupakan episentrum tertinggi.")
with c4:
    show_image("B7_paparan_sekolah.png", "Sangat banyak titik api yang berada dalam radius <5 km dari sekolah, mengancam anak-anak dengan risiko ISPA.")

st.markdown('<div class="section-title">Pertanyaan 3: Seberapa Parah Intensitas (Severity) Apinya?</div>', unsafe_allow_html=True)
c5, c6 = st.columns(2)
with c5:
    show_image("C2_frp_tier.png", "Mayoritas api berskala Rendah-Menengah. Prioritas pemadaman udara harus difokuskan pada tingkat Ekstrem.")
with c6:
    show_image("A2_siang_malam.png", "Api malam hari mengindikasikan karakteristik gambut membara (smoldering) yang sulit dipadamkan dan menghasilkan asap pekat.")

st.markdown('<div class="section-title">Pertanyaan 4: Area Mana yang Paling Mendesak Untuk Diselamatkan Saat Ini?</div>', unsafe_allow_html=True)
st.markdown("Menyatukan FRP (Intensitas), Jarak ke Sekolah (Keterpaparan), dan kepadatan penduduk, kami memformulasikan **Skor Risiko Komposit**.")
c7, c8 = st.columns([1,1])
with c7:
    show_image("E2_risiko_provinsi.png", "Distribusi titik berisiko Kritis di setiap provinsi.")
with c8:
    st.markdown('<br><div class="answer-box"><strong>Kesimpulan Tindakan Operasional (Sesuai Jawaban Inti):</strong><br><br><ul><li>🚁 <strong>~3.080 Titik Prioritas Udara</strong> (FRP Ekstrem > P95) yang mutlak butuh pengecekan jalur udara.</li><br><li>🚒 <strong>~49.418 Titik Assessment Sosial</strong> (Jarak Sekolah ≤ 5km) yang membutuhkan asesmen dampak terhadap komunitas terdekat.</li><br><li>Area dengan Skor Kritis absolut (100.0) mayoritas terpusat di Kalimantan Barat dan Kalimantan Tengah.</li></ul></div>', unsafe_allow_html=True)

st.markdown("### 🗺️ Simulasi Peta Prioritas Verifikasi")
st.markdown("Mengubah fragmentasi data menjadi satu peta prioritas (Titik Merah = Kritis).")

# Tampilkan Peta
if not df.empty and 'latitude' in df.columns and 'longitude' in df.columns:
    color_map = {'Kritis': '#DC2626', 'Tinggi': '#F97316', 'Sedang': '#FBBF24', 'Rendah': '#3B82F6'}
    
    # Ambil sample jika terlalu besar agar dashboard tetap responsif, atau tampilkan semua
    plot_df = df.copy()
    
    fig_map = px.scatter_mapbox(
        plot_df, lat="latitude", lon="longitude", color="risk_category" if 'risk_category' in plot_df.columns else None,
        hover_name="province_name", hover_data=["date_local", "frp", "dist_nearest_school_km"] if 'dist_nearest_school_km' in plot_df.columns else [],
        zoom=4.5, center={"lat": -1.0, "lon": 114.0},
        mapbox_style="open-street-map", color_discrete_map=color_map,
        title="Peta Titik Panas Berdasarkan Tingkat Risiko"
    )
    fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Data lokasi tidak tersedia.")

if not df.empty and 'verification_priority' in df.columns:
    st.markdown("### 📋 Simulasi Antrean Prioritas Tertinggi (Top 10)")
    st.markdown("Dari puluhan ribu titik, ini adalah 10 area yang harus dikerahkan bantuan HARI INI.")
    top_queue = df.sort_values(by='verification_priority', ascending=False).head(10)
    display_cols = ['date_local', 'province_name', 'latitude', 'longitude', 'frp', 'dist_nearest_school_km', 'verification_priority', 'risk_category']
    display_cols = [c for c in display_cols if c in top_queue.columns]
    
    show_df = top_queue[display_cols].copy()
    if 'date_local' in show_df.columns: show_df['date_local'] = show_df['date_local'].dt.strftime('%Y-%m-%d')
    if 'frp' in show_df.columns: show_df['frp'] = show_df['frp'].round(1)
    if 'dist_nearest_school_km' in show_df.columns: show_df['dist_nearest_school_km'] = show_df['dist_nearest_school_km'].round(2)
    
    st.dataframe(show_df, use_container_width=True, hide_index=True)
