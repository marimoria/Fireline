# FIRELINE — DSA Baseline dan MVP Prioritization

**Status: paket review Checkpoint 2, bukan hasil final.** Baca
[REVIEW_STATUS.md](REVIEW_STATUS.md) sebelum memakai angka untuk PRD.
Korelasi dan panel cuaca masih merupakan output sebelum penyelarasan waktu
FIRMS (UTC) dan NASA POWER (LST). Output tersebut belum dihitung ulang.
Skor prioritas tidak memakai cuaca; bobotnya tetap provisional.

Repository kerja ini menyusun bukti data untuk case study FIRELINE. Arah produknya
adalah **peta dan antrean area yang perlu diverifikasi**, bukan prediksi kebakaran
dan bukan sistem yang mengambil keputusan lapangan secara otomatis.

## Cara membaca alur analisis

### 1. Fondasi observasi

[EDA FIRMS pada branch Kaka](https://github.com/marimoria/Fireline/blob/eda-kaka/EDA_FIRMS_Hotspot.ipynb) adalah analisis dasar yang dirujuk, bukan disalin ke branch ini. Notebook ini
menjelaskan struktur, kualitas, distribusi waktu, distribusi lokasi, FRP,
confidence, serta batas interpretasi NASA FIRMS.

Satu baris FIRMS dibaca sebagai **observasi anomali panas oleh satelit**. Satu
baris tidak otomatis berarti satu kebakaran lapangan yang sudah terverifikasi.

### 2. Validasi dataset eksternal

**notebooks/02_FIRELINE_External_Data_Validation.ipynb** menguji NASA POWER Daily
pada periode yang sama dengan FIRMS. Notebook ini memeriksa kelengkapan data dan
hubungan eksploratif hujan, suhu, kelembapan, serta angin dengan jumlah observasi.

Korelasi pada output notebook adalah eksperimen sebelum koreksi UTC–LST,
bukan angka resmi untuk PRD. Kesamaan label tanggal tidak menjamin jendela
24 jam yang sama. Agregasi cuaca regional juga belum memakai mask daratan
lima provinsi; perhitungan dan interpretasinya perlu ditinjau ulang.

### 3. Pipeline MVP

**notebooks/03_FIRELINE_MVP_Priority_Pipeline.ipynb** merangkum observasi menjadi
unit grid_id + date, menambahkan label provinsi, konteks fasilitas, dan cuaca,
lalu membuat skor prioritas sinyal yang transparan.

Skor hanya memakai:

- aktivitas observasi hari ini: 40%;
- persistensi tujuh hari: 35%;
- intensitas FRP relatif: 25%.

Data sekolah dan cuaca sengaja tidak dimasukkan ke skor. Keduanya hanya muncul
sebagai konteks sampai manfaat dan bobotnya tervalidasi.

## Output utama

**mvp_outputs/lowfi_mvp_priority_dashboard.png** adalah rancangan dashboard DSA.
Angkanya berasal dari tanggal demo historis 3 September 2024 dan bukan feed live.
Panel cuaca pada gambar belum diperbarui setelah audit UTC–LST: jangan gunakan
sebagai hasil cuaca tervalidasi. Gambar ini hanya rancangan struktur dashboard.

**mvp_outputs/data_contract.json** menjelaskan unit data, kunci utama, input skor,
label prioritas, guardrail, dan struktur handoff konseptual untuk SEA.

**mvp_outputs/MVP_METHODOLOGY_AND_DATA_DICTIONARY.md** menjelaskan rumus, arti
kolom, kualitas data, dan hal yang tidak boleh diklaim.

**PRD_SUPPORTING_DATA_BILINGUAL.md** memisahkan ringkasan hasil, keterbatasan,
dan asumsi dalam Bahasa Indonesia dan Inggris. Korelasi cuaca belum masuk fakta PRD.

CSV hasil dan cache data mentah disimpan lokal serta tidak disiapkan untuk Git.
Branch ini hanya berisi dua notebook, dokumentasi, ringkasan JSON, dan gambar
dashboard. Versi sumber .py, naskah pribadi, dan hasil menjalankan ulang EDA
Kaka tidak disertakan. Riwayat branch berupa snapshot terpisah; main tidak diubah.

## Handoff lintas peran

- **PMA:** memakai fakta terverifikasi untuk problem statement dan mencatat
  manfaat operasional sebagai hipotesis.
- **UX:** memakai struktur informasi, status data, dan bahasa guardrail untuk
  wireframe.
- **SEA:** memakai grid_id + date dan data contract untuk rancangan sistem
  konseptual; API nyata tidak diwajibkan pada MVP ini.
- **DSA:** menjaga kualitas data, menguji kestabilan prioritas, dan baru memakai
  istilah prediksi setelah evaluasi berbasis waktu serta label target tersedia.

## Sumber

- NASA FIRMS VIIRS: https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html
- NASA POWER Daily API: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- BIG Batas Provinsi: https://geoservices.big.go.id/gis/rest/services/STIG/Batas_Provinsi/MapServer
- BMKG Data Terbuka: https://data.bmkg.go.id/
