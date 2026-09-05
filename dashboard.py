import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="FIRELINE: Prioritisasi Karhutla",
    layout="wide",
    page_icon="🔥",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    .kpi-label { font-size: 0.9rem; color: #6B7280; }
    .kpi-value { font-size: 1.9rem; font-weight: 800; color: #111827; line-height: 1.1; }
    .kpi-sub   { font-size: 0.78rem; color: #9CA3AF; margin-top: 2px; }
    .metric-card { padding: 14px 16px; border-radius: 8px; background: #F9FAFB;
                   border: 1px solid #E5E7EB; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
    .caption { font-size: 0.82rem; color: #6B7280; font-style: italic;
               margin-top: 4px; margin-bottom: 18px; line-height: 1.5; }
    .date-banner { background:#EFF6FF; border-left:4px solid #2980B9;
                   padding:10px 16px; border-radius:6px; margin-bottom:14px; font-size:0.9rem; }
</style>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    hp = os.path.join("data", "processed", "hotspot_scored_final.csv")
    cl = os.path.join("data", "processed", "climate_fire_fusion_SHIFTED_seasonal.csv")
    df_hp = pd.read_csv(hp) if os.path.exists(hp) else pd.DataFrame()
    df_cl = pd.read_csv(cl) if os.path.exists(cl) else pd.DataFrame()
    if not df_hp.empty:
        df_hp['date_local'] = pd.to_datetime(df_hp['date_local'])
    if not df_cl.empty:
        df_cl['date'] = pd.to_datetime(df_cl['date'])
    return df_hp, df_cl

df_all, df_climate = load_data()

if df_all.empty:
    st.error("Data `hotspot_scored_final.csv` tidak ditemukan. Jalankan semua notebook EDA terlebih dahulu.")
    st.stop()

# ── Color constants ───────────────────────────────────────────────────────────
C_RED    = "#C0392B"
C_ORANGE = "#E67E22"
C_YELLOW = "#F1C40F"
C_BLUE   = "#2980B9"
C_GREY   = "#7F8C8D"
RISK_COLORS   = {"Kritis": C_RED, "Tinggi": C_ORANGE, "Sedang": C_YELLOW, "Rendah": C_BLUE}
ORDERED_RISKS = ["Kritis", "Tinggi", "Sedang", "Rendah"]

# ══════════════════════════════════════════════════════════════════════════════
#  ❶  TERPUSAT: FILTER UTAMA (tanggal di atas halaman, bukan sidebar)
# ══════════════════════════════════════════════════════════════════════════════
st.title("🔥 FIRELINE: Prioritisasi Kebakaran Hutan Kalimantan")
st.markdown(
    "Menggabungkan data satelit NASA, lokasi sekolah, dan cuaca untuk menjawab: "
    "**Area mana yang harus diverifikasi hari ini?**"
)

date_min = df_all['date_local'].min().date()
date_max = df_all['date_local'].max().date()

col_date, col_prov, col_risk = st.columns([3, 3, 2])
with col_date:
    date_range = st.date_input(
        "📅 Rentang Tanggal — berlaku untuk SEMUA grafik",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )
with col_prov:
    prov_options = sorted(df_all['province_name'].dropna().unique())
    prov_filter = st.multiselect("🗺️ Provinsi", options=prov_options, default=prov_options)
with col_risk:
    risk_filter = st.multiselect("⚠️ Tingkat Risiko", options=ORDERED_RISKS, default=ORDERED_RISKS)

# Parse dates safely
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    d_start, d_end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    d_start, d_end = pd.Timestamp(date_min), pd.Timestamp(date_max)

st.markdown(
    f'<div class="date-banner">📌 Menampilkan data dari '
    f'<b>{d_start.strftime("%d %b %Y")}</b> hingga <b>{d_end.strftime("%d %b %Y")}</b></div>',
    unsafe_allow_html=True,
)

st.sidebar.markdown("### Panduan Kategori Risiko")
st.sidebar.markdown("""
Setiap titik api diberi skor berdasarkan tiga faktor:

1. **Pancaran Panas (FRP)** — semakin tinggi panas yang dipancarkan satelit, semakin besar skor.
2. **Jarak ke Sekolah Terdekat** — semakin dekat ke sekolah, semakin tinggi risiko dampak sosial.
3. **Musim Kemarau** — titik api saat kemarau mendapat pengganda ×1.5.

| Kategori | Artinya |
|---|---|
| 🔴 **Kritis** | FRP ekstrem (>P95) *atau* berjarak ≤5 km dari sekolah |
| 🟠 **Tinggi** | Skor gabungan berada di sepertiga atas non-Kritis |
| 🟡 **Sedang** | Skor di tengah-tengah |
| 🔵 **Rendah** | Skor paling kecil, risiko paling minimal |

> Skor ini bersifat eksploratif dan **belum divalidasi** dengan data lapangan.
""")

# ── Apply ALL filters (date + province + risk) ────────────────────────────────
fdf = df_all[
    (df_all['date_local'] >= d_start) &
    (df_all['date_local'] <= d_end)   &
    (df_all['risk_category'].isin(risk_filter)) &
    (df_all['province_name'].isin(prov_filter))
].copy()

# Dry month numbers from the FULL dataset (not just filtered)
dry_month_nums = set(df_all[df_all['is_dry_season']]['date_local'].dt.month.unique())

# ── KPIs ─────────────────────────────────────────────────────────────────────
st.markdown("---")

n_total  = len(fdf)
n_kritis = int((fdf['risk_category'] == 'Kritis').sum())
n_dekat  = int((fdf['dist_nearest_school_km'] < 5).sum())

# Peak month (reactive to date filter)
if not fdf.empty:
    peak_series = fdf.groupby(fdf['date_local'].dt.to_period('M')).size()
    peak_period = peak_series.idxmax()
    peak_count  = int(peak_series.max())
    peak_label  = peak_period.strftime("%b %Y")
else:
    peak_label, peak_count = "–", 0

pct_kritis = f"{n_kritis/n_total*100:.1f}%" if n_total > 0 else "–"
pct_dekat  = f"{n_dekat/n_total*100:.1f}%" if n_total > 0 else "–"

def kpi(label, value_str, sub="", color="#111827", border="transparent"):
    return (
        f'<div class="metric-card" style="border-left:5px solid {border};">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value" style="color:{color};">{value_str}</div>'
        f'<div class="kpi-sub">{sub}</div></div>'
    )

k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(kpi("📡 Total Titik Api Terdeteksi", f"{n_total:,}", f"{d_start.strftime('%d %b %Y')} – {d_end.strftime('%d %b %Y')}"), unsafe_allow_html=True)
with k2: st.markdown(kpi("🚨 Tingkat Risiko Kritis (P1)", f"{n_kritis:,}", f"{pct_kritis} dari total — butuh tindak lanjut segera", color=C_RED, border=C_RED), unsafe_allow_html=True)
with k3: st.markdown(kpi("🏫 Berdekatan dengan Sekolah (< 5 km)", f"{n_dekat:,}", f"{pct_dekat} dari total — potensi ancam anak-anak", color=C_ORANGE, border=C_ORANGE), unsafe_allow_html=True)
with k4: st.markdown(kpi("📅 Bulan Puncak Kebakaran", peak_label, f"{peak_count:,} titik api terdeteksi di bulan ini", color="#1E3A8A", border=C_BLUE), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  Baris 1 — Peta + Provinsi + Donut Risiko
# ══════════════════════════════════════════════════════════════════════════════
map_col, right_col = st.columns([6, 4])

with map_col:
    MAP_OPTIONS = {
        "📍 Sebaran Titik Prioritas": "scatter",
        "🔥 Kepadatan Jumlah Titik Api (Heatmap)": "density_count",
        "🌡️ Kepadatan Intensitas Pancaran Panas (Heatmap)": "density_frp",
    }
    map_choice = st.radio("Mode Peta:", list(MAP_OPTIONS.keys()), horizontal=True)
    mode = MAP_OPTIONS[map_choice]

    HEATMAP_SCALE = [
        [0.0,  "#FFFFB2"], [0.2,  "#FED976"], [0.4,  "#FEB24C"],
        [0.6,  "#FD8D3C"], [0.75, "#E31A1C"], [0.9,  "#800026"],
        [1.0,  "#000000"],
    ]

    MAP_CAPTIONS = {
        "scatter": (
            "Setiap titik adalah satu deteksi api dari satelit NASA. "
            "Warna merah = risiko <b>Kritis</b>, harus diverifikasi segera."
        ),
        "density_count": (
            "Peta menunjukkan di mana titik-titik api paling terkonsentrasi. "
            "Skala kanan (Sangat Jarang → Sangat Padat) adalah ukuran <i>relatif</i> — "
            "area hitam berarti <b>paling banyak</b> titik api di area tersebut "
            "dibanding seluruh wilayah lainnya."
        ),
        "density_frp": (
            "Peta menunjukkan di mana pancaran panas paling tinggi. "
            "Skala kanan (Sangat Rendah → Ekstrem) adalah ukuran <i>relatif</i> — "
            "area hitam berarti <b>api dengan panas paling intens</b>, "
            "kandidat utama untuk intervensi water bombing."
        ),
    }

    if not fdf.empty:
        if mode == "scatter":
            fdf['_hover'] = fdf.apply(
                lambda r: (
                    f"<b>{r['province_name']}</b><br>"
                    f"Tingkat Risiko: <b>{r['risk_category']}</b><br>"
                    f"Pancaran Panas: {r['frp']:.1f} MW<br>"
                    f"Jarak ke Sekolah Terdekat: {r['dist_nearest_school_km']:.1f} km<br>"
                    f"Tanggal: {pd.Timestamp(r['date_local']).strftime('%d %b %Y')}"
                ), axis=1,
            )
            fig_map = px.scatter_mapbox(
                fdf, lat="latitude", lon="longitude",
                color="risk_category", color_discrete_map=RISK_COLORS,
                custom_data=["_hover"],
                zoom=4.5, center={"lat": -1.0, "lon": 114.0},
                mapbox_style="carto-positron",
                category_orders={"risk_category": ORDERED_RISKS},
            )
            fig_map.update_traces(
                hovertemplate="%{customdata[0]}<extra></extra>",
                marker=dict(size=5, opacity=0.7),
            )
            fig_map.update_layout(
                title="Sebaran Lokasi Titik Api Terdeteksi",
                legend=dict(
                    orientation="h", yanchor="top", y=-0.05,
                    xanchor="left", x=0,
                    title_text="Tingkat Risiko:",
                    bgcolor="rgba(255,255,255,0.9)",
                ),
            )

        elif mode == "density_count":
            fig_map = px.density_mapbox(
                fdf, lat="latitude", lon="longitude",
                radius=14, zoom=4.5, center={"lat": -1.0, "lon": 114.0},
                mapbox_style="carto-positron",
                color_continuous_scale=HEATMAP_SCALE,
            )
            fig_map.update_coloraxes(
                colorbar=dict(
                    title=dict(text="Kepadatan Titik Api<br>(Indeks Relatif)", side="top"),
                    tickmode="auto",
                    tickformat=".1f",
                    len=0.75, thickness=15, tickfont=dict(size=11),
                )
            )
            fig_map.update_layout(
                title="Konsentrasi Titik Api — Kuning (Jarang) → Hitam (Paling Padat)"
            )

        else:  # density_frp
            fig_map = px.density_mapbox(
                fdf, lat="latitude", lon="longitude", z="frp",
                radius=14, zoom=4.5, center={"lat": -1.0, "lon": 114.0},
                mapbox_style="carto-positron",
                color_continuous_scale=HEATMAP_SCALE,
            )
            fig_map.update_coloraxes(
                colorbar=dict(
                    title=dict(text="Intensitas Pancaran<br>Panas (MW)", side="top"),
                    tickmode="auto",
                    tickformat=",.0f",
                    len=0.75, thickness=15, tickfont=dict(size=11),
                )
            )
            fig_map.update_layout(
                title="Intensitas Pancaran Panas (Fire Radiative Power) — Kuning (Rendah) → Hitam (Ekstrem)"
            )

        fig_map.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0}, height=540)
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown(f'<div class="caption">{MAP_CAPTIONS[mode]}</div>', unsafe_allow_html=True)
    else:
        st.warning("Tidak ada data untuk ditampilkan dengan filter saat ini.")

with right_col:
    # ── Bar Provinsi ──────────────────────────────────────────────────────────
    if not fdf.empty:
        prov_cnt = fdf['province_name'].value_counts().reset_index()
        prov_cnt.columns = ["Provinsi", "Jumlah"]
        total_p = prov_cnt['Jumlah'].sum()
        prov_cnt['Persen'] = (prov_cnt['Jumlah'] / total_p * 100).round(1)
        bar_colors = [C_RED if i < 2 else C_GREY for i in range(len(prov_cnt))]

        fig_prov = go.Figure(go.Bar(
            x=prov_cnt['Provinsi'],
            y=prov_cnt['Jumlah'],
            text=[f"{v:,}  ({p}%)" for v, p in zip(prov_cnt['Jumlah'], prov_cnt['Persen'])],
            textposition="outside",
            marker_color=bar_colors,
            hovertemplate="<b>%{x}</b><br>%{y:,} titik api terdeteksi<extra></extra>",
        ))
        fig_prov.update_layout(
            title="Total Titik Api per Provinsi<br><sup>Dua provinsi terbanyak disorot merah</sup>",
            xaxis_title="",
            yaxis_title="Jumlah Titik Api",
            yaxis=dict(showgrid=True, gridcolor="#F3F4F6"),
            margin={"r": 10, "t": 65, "l": 0, "b": 30},
            height=295,
            plot_bgcolor="white",
        )
        st.plotly_chart(fig_prov, use_container_width=True)
        st.markdown(
            '<div class="caption">Kalimantan Barat secara konsisten menanggung '
            'jumlah deteksi tertinggi dibanding provinsi lain di Kalimantan.</div>',
            unsafe_allow_html=True,
        )

    # ── Donut Risiko ──────────────────────────────────────────────────────────
    if not fdf.empty:
        risk_cnt = (
            fdf['risk_category']
            .value_counts()
            .reindex(ORDERED_RISKS)
            .dropna()
            .reset_index()
        )
        risk_cnt.columns = ["Kategori Risiko", "Jumlah"]

        fig_risk = px.pie(
            risk_cnt, values="Jumlah", names="Kategori Risiko",
            hole=0.5,
            color="Kategori Risiko",
            color_discrete_map=RISK_COLORS,
            category_orders={"Kategori Risiko": ORDERED_RISKS},
        )
        fig_risk.update_traces(
            # Show only percent inside slices — avoids label/title collision
            textinfo="percent",
            textfont_size=12,
            hovertemplate="<b>%{label}</b><br>%{value:,} titik api (%{percent})<extra></extra>",
        )
        fig_risk.update_layout(
            title=dict(text="Proporsi Tingkat Risiko Operasional", x=0, xanchor="left", pad=dict(t=0, b=10)),
            legend=dict(
                orientation="h",
                yanchor="top", y=-0.15,
                xanchor="left", x=0,
                title_text="",
                bgcolor="rgba(255,255,255,0)",
            ),
            margin={"r": 10, "t": 50, "l": 10, "b": 60},
            height=260,
        )
        st.plotly_chart(fig_risk, use_container_width=True)
        st.markdown(
            '<div class="caption">'
            '<b>Kritis</b>: Pancaran Panas sangat tinggi (>P95) <i>atau</i> berjarak ≤5 km dari sekolah. '
            '<b>Tinggi</b>: Sepertiga atas dari titik non-Kritis. '
            '<b>Sedang/Rendah</b>: Skor lebih kecil, prioritas lebih rendah.'
            '</div>',
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════════════════════════════════════
#  Baris 2 — Jarak ke Sekolah + Curah Hujan vs Titik Api
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
col_dist, col_clim = st.columns(2)

with col_dist:
    if not fdf.empty:
        bins   = [-0.01, 2, 5, 10, 50, 99999]
        labels = ["< 2 km", "2–5 km", "5–10 km", "10–50 km", "> 50 km"]
        fdf_d  = fdf.copy()
        fdf_d['Jarak'] = pd.cut(fdf_d['dist_nearest_school_km'], bins=bins, labels=labels)
        dist_cnt = fdf_d['Jarak'].value_counts().reindex(labels).reset_index()
        dist_cnt.columns = ["Jarak ke Sekolah", "Jumlah"]
        d_colors = [C_RED, C_RED, C_ORANGE, C_GREY, C_GREY]

        fig_dist = go.Figure(go.Bar(
            x=dist_cnt['Jarak ke Sekolah'],
            y=dist_cnt['Jumlah'],
            text=[f"{v:,}" for v in dist_cnt['Jumlah']],
            textposition="outside",
            marker_color=d_colors,
            hovertemplate="<b>Radius %{x}</b><br>%{y:,} titik api di rentang ini<extra></extra>",
        ))
        fig_dist.update_layout(
            title="Seberapa Dekat Api dengan Sekolah?<br><sup>Merah = zona berbahaya bagi anak-anak</sup>",
            xaxis_title="Jarak ke Sekolah Terdekat",
            yaxis_title="Jumlah Titik Api",
            yaxis=dict(showgrid=True, gridcolor="#F3F4F6"),
            margin={"r": 10, "t": 65, "l": 0, "b": 30},
            height=340, plot_bgcolor="white",
        )
        st.plotly_chart(fig_dist, use_container_width=True)
        st.markdown(
            '<div class="caption">Titik api dalam radius 2–5 km dari sekolah (ditandai merah) '
            'dapat menyebabkan paparan asap yang berdampak langsung pada kesehatan anak-anak.</div>',
            unsafe_allow_html=True,
        )

with col_clim:
    if not df_climate.empty:
        cl = df_climate[
            (df_climate['date'] >= d_start) &
            (df_climate['date'] <= d_end)
        ].copy()

        if not cl.empty:
            clim_grp = (
                cl.groupby(cl['date'].dt.to_period('M'))
                  .agg(curah_hujan=('RR', 'mean'), jumlah_titik_api=('hotspot_count', 'sum'))
                  .reset_index()
            )
            clim_grp['Bulan'] = clim_grp['date'].dt.to_timestamp()

            fig_clim = go.Figure()
            fig_clim.add_trace(go.Bar(
                x=clim_grp['Bulan'], y=clim_grp['curah_hujan'],
                name="Rata-rata Curah Hujan (mm/hari)",
                marker_color=C_BLUE, opacity=0.5,
                hovertemplate="<b>%{x|%b %Y}</b><br>Curah Hujan: %{y:.1f} mm/hari<extra></extra>",
                yaxis="y2",
            ))
            fig_clim.add_trace(go.Scatter(
                x=clim_grp['Bulan'], y=clim_grp['jumlah_titik_api'],
                name="Jumlah Titik Api",
                line=dict(color=C_RED, width=3),
                hovertemplate="<b>%{x|%b %Y}</b><br>Titik Api Terdeteksi: %{y:,}<extra></extra>",
            ))
            fig_clim.update_layout(
                title="Curah Hujan vs Jumlah Titik Api per Bulan<br><sup>Mengapa prediksi berbasis cuaca saja tidak cukup?</sup>",
                yaxis=dict(title="Jumlah Titik Api", side="left", showgrid=False),
                yaxis2=dict(title="Curah Hujan (mm/hari)", side="right", overlaying="y", showgrid=False),
                xaxis=dict(
                    title="",
                    dtick="M1",
                    tickformat="%b %Y",
                    tickangle=-45,
                ),
                legend=dict(
                    orientation="h", yanchor="bottom", y=-0.45,
                    xanchor="left", x=0,
                    bgcolor="rgba(255,255,255,0.9)",
                ),
                margin={"r": 60, "t": 65, "l": 0, "b": 90},
                height=340, plot_bgcolor="white",
            )
            st.plotly_chart(fig_clim, use_container_width=True)
            st.markdown(
                '<div class="caption">Saat curah hujan turun drastis, jumlah titik api melonjak — '
                'namun jeda waktunya tidak konsisten antar tahun. Inilah mengapa model prediksi '
                'berbasis cuaca saja tidak bisa diandalkan untuk operasi harian.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("Tidak ada data cuaca di rentang tanggal ini.")
    else:
        st.warning("Data cuaca tidak tersedia.")

# ══════════════════════════════════════════════════════════════════════════════
#  Baris 3 — Tren Waktu + Tabel Prioritas
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
trend_col, table_col = st.columns([6, 4])

with trend_col:
    view_toggle = st.radio("Tampilkan tren per:", ["Hari", "Bulan"], horizontal=True)

    if not fdf.empty:
        if view_toggle == "Bulan":
            # --- Monthly bar chart — replicate 3.py logic exactly ---
            td = fdf.groupby(fdf['date_local'].dt.to_period('M')).size().reset_index(name='Jumlah')
            td['month_num'] = td['date_local'].dt.month
            # A month is kemarau if its month number appears in dry_month_nums
            td['is_dry'] = td['month_num'].isin(dry_month_nums)
            td['x_axis'] = td['date_local'].dt.to_timestamp()
            bar_colors = [C_RED if d else C_GREY for d in td['is_dry']]

            # Invisible traces for legend
            fig_trend = go.Figure([
                go.Bar(
                    x=td['x_axis'], y=td['Jumlah'],
                    marker_color=bar_colors,
                    text=[f"{v:,}" for v in td['Jumlah']],
                    textposition="outside",
                    textfont=dict(size=9),
                    hovertemplate="<b>%{x|%b %Y}</b><br>Total Titik Api: %{y:,}<extra></extra>",
                    showlegend=False,
                ),
                go.Bar(x=[], y=[], name="Musim Kemarau Aktual", marker_color=C_RED, showlegend=True),
                go.Bar(x=[], y=[], name="Musim Hujan", marker_color=C_GREY, showlegend=True),
            ])
            fig_trend.update_layout(
                title="Total Titik Api per Bulan — Merah = Bulan Musim Kemarau Aktual",
                xaxis=dict(
                    title="Bulan",
                    dtick="M1",
                    tickformat="%b %Y",
                    tickangle=-45,
                ),
                yaxis=dict(title="Total Titik Api", showgrid=True, gridcolor="#F3F4F6"),
                legend=dict(
                    orientation="h", yanchor="bottom", y=-0.45,
                    xanchor="left", x=0,
                ),
                margin={"r": 10, "t": 50, "l": 0, "b": 90},
                height=390, plot_bgcolor="white",
            )
            caption_trend = (
                "Warna merah menandai bulan-bulan yang tercatat sebagai Musim Kemarau Aktual "
                "berdasarkan data historis (kolom <i>is_dry_season</i> dari dataset FIRMS). "
                "Lonjakan deteksi hampir selalu bertepatan dengan bulan kemarau."
            )

        else:  # Harian
            td = fdf.groupby('date_local').size().reset_index(name='Jumlah')
            td['MA7'] = td['Jumlah'].rolling(7, min_periods=1).mean()

            fig_trend = go.Figure()
            fig_trend.add_trace(go.Bar(
                x=td['date_local'], y=td['Jumlah'],
                name="Harian",
                marker_color=C_RED, opacity=0.35,
                hovertemplate="<b>%{x|%d %b %Y}</b><br>%{y:,} titik api hari ini<extra></extra>",
            ))
            fig_trend.add_trace(go.Scatter(
                x=td['date_local'], y=td['MA7'],
                name="Rata-rata 7 hari",
                line=dict(color=C_RED, width=2.5),
                hovertemplate="<b>%{x|%d %b %Y}</b><br>Rata-rata 7 hari: %{y:.0f} titik<extra></extra>",
            ))
            # Dry season shading — use the data range visible
            if dry_month_nums:
                # Shade each year's dry months that fall within d_start..d_end
                for yr in range(d_start.year, d_end.year + 1):
                    for mo in sorted(dry_month_nums):
                        shade_s = pd.Timestamp(yr, mo, 1)
                        import calendar
                        shade_e = pd.Timestamp(yr, mo, calendar.monthrange(yr, mo)[1])
                        if shade_e < d_start or shade_s > d_end:
                            continue
                        fig_trend.add_vrect(
                            x0=max(shade_s, d_start), x1=min(shade_e, d_end),
                            fillcolor=C_ORANGE, opacity=0.12, layer="below", line_width=0,
                        )
            # Single annotation for the shading
            fig_trend.add_trace(go.Scatter(
                x=[None], y=[None], mode="markers",
                marker=dict(color=C_ORANGE, opacity=0.5, size=14, symbol="square"),
                name="Musim Kemarau Aktual",
            ))
            fig_trend.update_layout(
                title="Jumlah Titik Api per Hari di Kalimantan",
                xaxis=dict(title="Tanggal", showgrid=False),
                yaxis=dict(title="Jumlah Titik Api Terdeteksi", showgrid=True, gridcolor="#F3F4F6"),
                legend=dict(
                    orientation="h", yanchor="bottom", y=-0.35,
                    xanchor="left", x=0,
                ),
                margin={"r": 10, "t": 50, "l": 0, "b": 70},
                height=390, plot_bgcolor="white",
            )
            caption_trend = (
                "Area jingga menandai bulan-bulan Musim Kemarau Aktual "
                "(ditentukan dari histori bulan <i>is_dry_season</i> di data FIRMS). "
                "Garis merah tebal adalah rata-rata bergulir 7 hari untuk melicinkan fluktuasi harian."
            )

        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown(f'<div class="caption">{caption_trend}</div>', unsafe_allow_html=True)
    else:
        st.info("Tidak ada data di rentang waktu ini.")

with table_col:
    st.markdown("#### 📋 10 Area Paling Mendesak untuk Diverifikasi")
    if not fdf.empty and 'verification_priority' in fdf.columns:
        top10 = fdf.sort_values('verification_priority', ascending=False).head(10)
        show_cols = ['date_local', 'province_name', 'frp', 'dist_nearest_school_km', 'risk_category', 'verification_priority']
        show_cols = [c for c in show_cols if c in top10.columns]
        tdf = top10[show_cols].copy()
        if 'date_local'             in tdf.columns: tdf['date_local']             = tdf['date_local'].dt.strftime('%d %b %Y')
        if 'frp'                    in tdf.columns: tdf['frp']                    = tdf['frp'].round(1)
        if 'dist_nearest_school_km' in tdf.columns: tdf['dist_nearest_school_km'] = tdf['dist_nearest_school_km'].round(1)
        if 'verification_priority'  in tdf.columns: tdf['verification_priority']  = tdf['verification_priority'].round(1)

        tdf = tdf.rename(columns={
            'date_local':             'Tanggal',
            'province_name':          'Provinsi',
            'frp':                    'Pancaran Panas (MW)',
            'dist_nearest_school_km': 'Jarak Sekolah (km)',
            'risk_category':          'Risiko',
            'verification_priority':  'Skor Prioritas',
        })
        st.dataframe(tdf, use_container_width=True, height=360, hide_index=True)
        st.markdown(
            '<div class="caption">Daftar ini diurutkan otomatis dari Skor Prioritas tertinggi. '
            'Semakin tinggi skor, semakin mendesak titik tersebut diverifikasi di lapangan.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Tidak ada data prioritas untuk ditampilkan.")
