# Supporting Data — FIRELINE Checkpoint 2 (review)

Ringkasan memakai output pipeline Checkpoint 2 yang tersimpan, bukan perhitungan
ulang baseline v2. Jangan mencampur unit observasi mentah dan grid-hari.
Korelasi cuaca dikeluarkan dari fakta PRD sampai koreksi UTC–LST selesai.
Rincian batas analisis: [REVIEW_STATUS.md](REVIEW_STATUS.md).

## Bahasa Indonesia

| Temuan | Angka | Sumber | Maknanya |
|---|---|---|---|
| Observasi tidak merata menurut bulan dalam dataset ini | Juni–Oktober 83,42%; September 42,20% dari seluruh observasi yang tersedia | Dataset utama NASA FIRMS VIIRS NOAA-20; EDA branch eda-kaka | Mendukung eksplorasi tren dan filter tanggal. Cakupan 2024 dan 2026 parsial; belum membuktikan pola musim berulang atau beban petugas. |
| Ada tanggal dengan volume observasi tinggi | 2.400 observasi pada 3 September 2024 | NASA FIRMS; EDA branch eda-kaka | Menjadi alasan menguji ringkasan area; bukan 2.400 kebakaran berbeda dan bukan bukti keterlambatan verifikasi. |
| Data dapat diringkas menjadi unit area–tanggal | 61.583 observasi; 2.954 grid; 27.411 grid-hari | Notebook 03; pipeline_summary.json | Menyediakan unit konsisten untuk peta dan antrean. Penghematan waktu pengguna belum diukur. |
| Pelabelan provinsi masih memiliki celah | 97,10% grid-hari berlabel; 796 grid-hari tanpa label | BIG Batas Provinsi; spatial join notebook 03 | Tampilkan status data terbatas; ketidakcocokan bukan bukti bahwa seluruh area tersebut berada di luar Kalimantan. |
| Kelengkapan tanggal cuaca belum berarti kesamaan jendela waktu | Empat variabel tersedia pada label 669 tanggal; FIRMS UTC, cache POWER LST | NASA POWER; audit notebook 02 dan 03 | Penyelarasan waktu dan domain spasial perlu diperbaiki sebelum korelasi atau cuaca harian dipakai sebagai fakta produk. |
| Kedekatan sekolah memberi konteks lokasi | Median 2,94 km atas baris grid-hari, memakai jarak pusat grid ke sekolah terdekat | Indonesia School Dataset; notebook 03 | Jarak grid yang sama berulang per tanggal aktif. Bukan median grid unik, jarak tiap deteksi, atau bukti sekolah terdampak. |
| Prioritas masih sensitif terhadap pilihan komponen | Jaccard keanggotaan P1 0,555–0,639 pada uji penghapusan satu komponen | Uji ablation notebook 03 | Bobot 40/35/25 dan ambang P1 bersifat provisional; bukan ukuran akurasi atau probabilitas kebakaran. |

## English

| Finding | Figure | Source | What it means |
|---|---|---|---|
| Observations are unevenly distributed across months in this dataset | June–October: 83.42%; September: 42.20% of available observations | Main NASA FIRMS VIIRS NOAA-20 dataset; eda-kaka branch EDA | Supports exploring trends and date filters. Partial 2024/2026 coverage prevents treating pooled shares as evidence of recurring seasonality or staff workload. |
| Some dates have high observation volume | 2,400 observations on 3 September 2024 | NASA FIRMS; eda-kaka branch EDA | Motivates testing area summaries; does not mean 2,400 distinct fires or prove verification delays. |
| Observations can be summarized into area–date units | 61,583 observations; 2,954 grids; 27,411 grid-day rows | Notebook 03; pipeline_summary.json | Provides a consistent unit for maps and queues. User time savings have not been measured. |
| Province labeling still has coverage gaps | 97.10% of grid-day rows labeled; 796 unlabeled | BIG Province Boundaries; notebook 03 spatial join | Show data-limited status. Unmatched rows do not establish that all those areas lie outside Kalimantan. |
| Weather date completeness does not establish aligned daily windows | Four variables cover 669 date labels; FIRMS UTC versus cached POWER LST | NASA POWER; notebooks 02/03 audit | Time alignment and spatial-domain review are required before weather correlations become product evidence. |
| School proximity provides geographic context | Median 2.94 km across grid-day rows, using grid-center distance to the nearest school | Indonesia School Dataset; notebook 03 | Each grid distance is repeated for every active date. This is not a unique-grid median, detection-level distance, or evidence of school impact. |
| Priority membership remains sensitive to component choice | P1 membership Jaccard: 0.555–0.639 when one component is removed | Notebook 03 ablation test | The 40/35/25 weights and P1 thresholds remain provisional, not accuracy or fire-probability estimates. |

## Sources / Sumber

- Main data: case-study CSV, documented by [NASA FIRMS VIIRS](https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html).
- Baseline exploration: [Kaka branch](https://github.com/marimoria/Fireline/tree/eda-kaka).
- External audit: [Notebook 02](notebooks/02_FIRELINE_External_Data_Validation.ipynb).
- MVP calculation: [Notebook 03](notebooks/03_FIRELINE_MVP_Priority_Pipeline.ipynb) and [summary](mvp_outputs/pipeline_summary.json).
- Weather: [NASA POWER Daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/).
- Boundaries: [BIG Batas Provinsi](https://geoservices.big.go.id/gis/rest/services/STIG/Batas_Provinsi/MapServer).
- Schools: [Indonesia School Dataset](https://www.kaggle.com/datasets/marchotridyo/indonesia-school-dataset-with-province-data), local complete_data.csv.

## Assumptions requiring validation / Asumsi yang perlu divalidasi

- Antrean mempercepat verifikasi / A priority queue reduces verification time.
- Informasi sekolah membantu keputusan / School context improves user decisions.
- Cuaca meningkatkan prioritas / Weather improves prioritization.
- Petugas membutuhkan integrasi data / Operators need integrated information.
- Verifikasi memerlukan 12–24 jam atau pesan terlambat / Verification takes 12–24 hours or alerts arrive late.

Klaim operasional tersebut membutuhkan riset pengguna atau sumber operasional
terpisah. Tidak dapat dibuktikan hanya dari FIRMS, skor buatan, atau jarak sekolah.
These operational claims require separate user research or operational evidence.
