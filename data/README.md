# Data Lokal FIRELINE

Dataset CSV dan cache mentah tidak disiapkan untuk Git.

| Lokasi lokal | Sumber | Keterangan |
|---|---|---|
| fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv | Dataset utama case study / NASA FIRMS | Acuan utama |
| data/external/schools/complete_data.csv | Indonesia School Dataset | Konteks fasilitas saja |
| data/external/raw/nasa_power/ | NASA POWER Daily API | Cache cuaca 2024–2026 |
| data/external/raw/big/kalimantan_provinces.geojson | BIG Batas Provinsi MapServer | Lima provinsi Kalimantan |

Jika file cache NASA POWER belum tersedia, jalankan notebook 02 sebelum notebook 03.
Jika file sekolah belum tersedia, unduh dataset sekolah pendukung dan simpan memakai
nama serta lokasi yang tercantum di atas.
