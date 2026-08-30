# FIRELINE: Karhutla Risk Intelligence Platform
## Laporan Analisis Data Eksploratif (EDA) dan Fondasi Problem Statement

Platform intelijen risiko kebakaran hutan dan lahan (karhutla) berbasis data satelit, iklim, dan infrastruktur untuk mendukung pengambilan keputusan operasional penanganan karhutla di Kalimantan.

> **Tentang Dokumen Ini:** Dokumen ini disusun sebagai laporan EDA komprehensif untuk peran Data Scientist dalam proyek FIRELINE di COMPFEST 18 DSA. Setiap tahapan pemrosesan, setiap keputusan desain, dan setiap insight yang ditemukan dijelaskan bukan hanya *apa* hasilnya, tetapi *mengapa* insight itu penting dan *bagaimana* ia memengaruhi arah solusi yang kami bangun.

---

## Latar Belakang dan Konteks Permasalahan

### Mengapa Ini Bukan Sekadar Masalah Titik Api di Peta

Setiap musim kemarau, Kalimantan menghadapi krisis yang bersifat multidimensional. Data NASA FIRMS yang kami gunakan mencatat lebih dari **57.785 deteksi titik panas aktif** di Kalimantan dalam rentang Agustus 2024 hingga Juni 2026. Di balik angka itu, ada realita yang jauh lebih berat:

Kalimantan Barat saja mencatat **28.680 hektare** lahan hangus dalam satu musim kemarau. Bandara Singkawang terpaksa menangguhkan operasional akibat jarak pandang di bawah batas aman karena kabut asap. Kasus Infeksi Saluran Pernapasan Akut (ISPA) melonjak di kota-kota besar. Ini bukan krisis data — ini krisis **waktu dan prioritas**.

Masalah sesungguhnya bukan kurangnya data. BMKG menyediakan data cuaca, NASA FIRMS menyediakan titik panas aktif secara near-real-time, pemerintah daerah memiliki peta administrasi. Masalahnya adalah **fragmentasi informasi yang parah**: semua data ini hidup di platform yang berbeda, tidak saling bicara, dan tidak memberikan satu jawaban terintegrasi yang bisa langsung ditindaklanjuti.

Akibatnya: petugas lapangan bekerja tanpa panduan prioritas yang jelas. Rata-rata waktu verifikasi lapangan memakan **12-24 jam**, sementara api bisa menyebar dalam hitungan jam. Satu titik api kecil dekat sekolah atau permukiman padat bisa jauh lebih berbahaya daripada titik api besar di lahan kosong — tapi tanpa integrasi data spasial, petugas rentan **salah menetapkan prioritas**.

### Empat Pertanyaan yang Harus Dijawab Secara Cepat dan Tepat

FIRELINE didirikan untuk menjawab empat pertanyaan operasional berikut secara presisi dan otomatis:

1. **Area mana yang paling mendesak untuk diselamatkan saat ini?**
2. **Siapa populasi yang paling rentan terpapar?**
3. **Laporan mana yang harus diverifikasi lebih dahulu?**
4. **Respons apa yang harus diprioritaskan pertama kali?**

Seluruh pipeline EDA yang dijelaskan di dokumen ini adalah fondasi ilmiah untuk menjawab keempat pertanyaan tersebut.

---

## Inventaris Dataset: File Mentah yang Digunakan dan Tujuannya

Berikut adalah **semua file mentah** yang digunakan, dari mana asalnya, dan peran konkretnya dalam pipeline.

### Dataset Utama (Wajib)

**File:** `data/raw/Fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv`  
**Sumber:** NASA FIRMS (Fire Information for Resource Management System) — Sensor VIIRS di satelit NOAA-20  
**Isi:** 60.000+ baris data deteksi titik panas aktif dengan kolom: `latitude`, `longitude`, `acq_date`, `acq_time`, `satellite`, `confidence`, `brightness`, `frp`, `scan`, `track`, `instrument`, `version`, `daynight`  
**Peran dalam Pipeline:**  
- Kolom `frp` (Fire Radiative Power, dalam Megawatt) adalah ukuran intensitas api dari satelit. Ini adalah sinyal utama model risiko.  
- Kolom `confidence` (`l`/`n`/`h`) menunjukkan seberapa yakin algoritma satelit bahwa deteksi ini adalah api sungguhan (bukan pantulan panas industri, bangunan, atau anomali lain).  
- Kolom `daynight` memisahkan deteksi siang (`D`) dan malam (`N`), yang memiliki interpretasi fisik berbeda seperti yang akan dijelaskan di Modul A.

### Dataset Pendukung yang Dipilih

**File:** `data/raw/indonesia-province-jml-penduduk.json` & `data/raw/province_detail.csv`  
**Sumber:** Kaggle — `farizdarari/indonesia-province-jml-penduduk`  
**Isi:** Poligon batas wilayah administrasi provinsi Indonesia dengan data populasi terkait  
**Peran:** Digunakan untuk Spatial Join — mengetahui setiap titik api jatuh di provinsi mana. Populasi provinsi menjadi komponen pengganda dalam model risiko (area berpopulasi padat = risiko lebih tinggi).

**File:** `data/raw/climate_data.csv`  
**Sumber:** Kaggle — `greegtitan/indonesia-climate` (BMKG Historis)  
**Isi:** Data iklim harian dari stasiun-stasiun BMKG seluruh Indonesia tahun 2010-2020, mencakup kolom `Tn` (suhu minimum), `Tx` (suhu maksimum), `Tavg` (suhu rata-rata), `RH_avg` (kelembaban), `RR` (curah hujan), `ss` (durasi sinar matahari)  
**Peran:** Digunakan untuk membangun model korelasi cuaca-kebakaran. Dataset ini digunakan sebagai representasi pola iklim musiman (bukan sebagai data real-time) karena data cuaca 2024-2026 yang presisi tidak tersedia secara lokal.

**File:** `data/raw/pontianak_weather_daily_2021_2024.csv`  
**Sumber:** Kaggle — `royandika/pontianak-weather-daily-2021-2024`  
**Isi:** Data cuaca harian kota Pontianak (ibu kota Kalimantan Barat) tahun 2021-2024, kolom: `date`, `day`, `TAVG`, `RH_AVG`, `RR`  
**Peran:** Digunakan sebagai representasi cuaca Kalimantan Barat karena Pontianak adalah kota pusat di provinsi dengan kebakaran terbanyak. Satu-satunya dataset cuaca yang overlap langsung dengan periode hotspot.

**File:** Dataset Sekolah Indonesia (OSM/BPS)  
**Sumber:** Kaggle — `marchotridyo/indonesia-school-dataset-with-province-data`  
**Isi:** Koordinat latitude/longitude titik lokasi sekolah di Kalimantan  
**Peran:** Digunakan sebagai *proxy* kerentanan masyarakat. Mengapa sekolah? Karena: (1) sekolah adalah indikator kepadatan permukiman — di mana ada sekolah, ada komunitas; (2) sekolah mewakili populasi rentan (anak-anak); (3) penutupan sekolah akibat asap adalah dampak yang terukur dan langsung.

**File:** `data/raw/station_detail.csv`  
**Isi:** Detail stasiun cuaca BMKG: ID stasiun, nama, koordinat  
**Peran:** Menghubungkan setiap titik api ke stasiun cuaca terdekat untuk membangun tabel gabungan (fusion) iklim-kebakaran.

### Output yang Dihasilkan Sepanjang Pipeline

| File Output | Dibuat Oleh | Isi |
|---|---|---|
| `data/processed/hotspot_cleaned.csv` | Notebook 01 | Data hotspot setelah filter koordinat, waktu, dan tipe vegetasi |
| `data/processed/hotspot_master.csv` | Notebook 02 | Data master dengan semua fitur hasil rekayasa (jarak sekolah, provinsi, dll) |
| `data/processed/climate_fire_fusion.csv` | Notebook 02 | Tabel gabungan data iklim harian per stasiun dengan hitungan hotspot harian |
| `data/processed/hotspot_scored_final.csv` | Notebook 04 | Data final dengan Skor Risiko Komposit dan kategori (Rendah/Sedang/Tinggi/Kritis) |
| `outputs/core_questions_answers.md` | Notebook 04 | Jawaban 4 pertanyaan operasional berdasarkan data aktual |
| `outputs/figures/*.png` | Notebook 03 & 04 | 14 grafik hasil EDA |

---

## Alur Kerja Pipeline (Notebook 01 sampai 04)

```
[Notebook 01: Audit dan Pemahaman Data Mentah]
      |
      |-- Muat data dari CSV mentah NASA FIRMS
      |-- Validasi kualitas: cek missing values, tipe data, duplikasi
      |-- Konversi waktu UTC --> WIB (UTC+7) untuk akurasi temporal
      |-- Filter: buang titik yang bukan vegetasi (type != 0)
      |-- Filter: buang koordinat di luar bounding box Kalimantan
      |-- Simpan: hotspot_cleaned.csv
      |
      v
[Notebook 02: Persiapan Data dan Rekayasa Fitur]
      |
      |-- Spatial Join: pasangkan setiap titik api ke poligon provinsi (geopandas)
      |-- Fitur baru: frp_log (log(1+FRP) untuk normalisasi distribusi skewed)
      |-- Fitur baru: frp_tier (Rendah/Menengah/Tinggi/Ekstrem berdasarkan kuartil)
      |-- Fitur baru: is_dry_season (True jika bulan 6-10, False selainnya)
      |-- Kalkulasi BallTree Haversine: jarak terdekat ke sekolah untuk tiap titik api
      |-- Pasangkan stasiun cuaca terdekat (BallTree Haversine)
      |-- Gabungkan (merge) data iklim harian dengan agregasi hotspot per stasiun
      |-- Simpan: hotspot_master.csv, climate_fire_fusion.csv
      |
      v
[Notebook 03: Analisis Data Eksploratif (EDA)]
      |
      |-- Modul A: Analisis temporal (kapan?)
      |-- Modul B: Analisis spasial dan keterpaparan sekolah (di mana, siapa?)
      |-- Modul C: Distribusi intensitas FRP (seberapa parah?)
      |-- Modul D: Korelasi cuaca dan kebakaran (mengapa dan bisa diprediksi?)
      |-- Hasilkan 12 grafik, simpan ke outputs/figures/
      |
      v
[Notebook 04: Indeks Komposit dan Penilaian Risiko]
      |
      |-- Normalisasi FRP --> skor 0-100
      |-- Hitung exposure_score dari jarak ke sekolah (makin dekat = makin tinggi)
      |-- Hitung base_score = (0.6 x FRP score) + (0.4 x exposure score)
      |-- Terapkan pengganda populasi (0.8 - 1.2x) berdasarkan kepadatan provinsi
      |-- Terapkan pengganda musim (1.0 normal, 1.5x selama musim kemarau)
      |-- Kategorikan: Rendah/Sedang/Tinggi/Kritis
      |-- Hitung verification_priority = risk_score x confidence_weight
      |-- Simpan: hotspot_scored_final.csv
      |-- Jawab 4 pertanyaan operasional ke core_questions_answers.md
```

---

## Penjelasan Detail Tiap Tahap

### Notebook 01: Audit Data Mentah

Sebelum menganalisis apapun, data harus dipastikan bersih dan bermakna.

**Konversi Waktu (UTC ke WIB)**

Data NASA FIRMS menggunakan waktu UTC standar. Kalimantan menggunakan WIB (UTC+7) dan WITA (UTC+8). Semua timestamp dikonversi ke waktu lokal. Ini bukan detail teknis semata — tanpa konversi ini, analisis "siang vs malam" akan keliru karena batas siang/malam bergeser 7 jam dari realita lapangan.

**Filter Tipe Kebakaran**

Kolom `type` membedakan: 0 = vegetasi/lahan, 1 = gunung berapi aktif, 2 = sumber statis (industri, perkotaan), 3 = lainnya. Kami hanya mempertahankan `type == 0` karena target analisis adalah kebakaran hutan dan lahan, bukan anomali panas industri.

**Filter Koordinat Kalimantan**

Bounding box: lintang -5.0 sampai 7.7, bujur 108.5 sampai 119.5. Sebanyak 69 titik berada di luar batas ini (kemungkinan error GPS atau koordinat di perairan) dan dibuang. Data bersih: **57.785 titik api valid**.

**Distribusi per Tahun**

| Tahun | Jumlah Titik | Catatan |
|---|---|---|
| 2024 | 23.046 | Data mulai Agustus 2024 (bukan awal tahun) |
| 2025 | 28.398 | Data penuh satu tahun |
| 2026 | 6.341 | Data hanya sampai Juni 2026 |

*Catatan kritis:* Perbandingan langsung 2024 vs 2025 tidak bisa dilakukan karena data 2024 hanya mencakup Agustus-Desember (5 bulan), sementara 2025 mencakup penuh 12 bulan. Untuk bulan yang sebanding (Agustus-Desember), 2024 memiliki 19.050 titik sementara 2025 memiliki 19.190 titik — tidak ada lonjakan signifikan pada periode yang setara.

---

### Notebook 02: Rekayasa Fitur

**Spatial Join ke Provinsi**

Menggunakan `geopandas.sjoin()` dengan poligon batas provinsi. Dari 57.785 titik, 57.716 berhasil dipetakan ke provinsi. 69 titik sisanya kemungkinan berada di perairan atau wilayah perbatasan dan dibuang di langkah sebelumnya.

**Algoritma BallTree Haversine untuk Jarak Sekolah**

Untuk menghitung jarak dari 57.785 titik api ke ribuan titik sekolah secara efisien, digunakan algoritma BallTree dengan metrik haversine. BallTree adalah struktur data pohon yang mempartisi titik-titik koordinat ke dalam bola (*ball*) bersarang, memungkinkan pencarian *k-nearest neighbor* jauh lebih cepat daripada perhitungan jarak brute-force O(n*m). Metrik haversine menghitung jarak lingkaran besar di permukaan bumi, akurat untuk koordinat geografis tanpa memerlukan proyeksi.

Rata-rata jarak ke sekolah terdekat: **3,48 km** (median: 2,71 km). Distribusi sangat right-skewed — mayoritas titik api dekat sekali dengan sekolah.

**Rekayasa Fitur frp_tier**

FRP memiliki distribusi sangat ekstrem. Daripada bekerja dengan angka mentah, dibuat kategori berbasis kuartil untuk memudahkan analisis dan komunikasi:

| Tier | Definisi | Jumlah | Pct |
|---|---|---|---|
| Rendah | Bawah Q1 (< ~5 MW) | 14.442 | 25% |
| Menengah | Q1 - Q3 (5 - 12 MW) | 28.889 | 50% |
| Tinggi | Q3 - P95 (12 - 34 MW) | 11.564 | 20% |
| Ekstrem | Di atas P95 (> 34 MW) | 2.890 | 5% |

**Penanda Musim Kemarau (is_dry_season)**

Berdasarkan pola iklim Indonesia, musim kemarau di Kalimantan jatuh pada bulan Juni hingga Oktober. Variabel biner ini digunakan sebagai pengganda (1.5x) dalam model risiko, karena api yang terjadi saat musim kemarau memiliki risiko penyebaran yang jauh lebih tinggi dibandingkan saat musim hujan.

---

### Notebook 03: Analisis Data Eksploratif

#### Modul A: Tren Temporal — Kapan Api Muncul dan Mengapa Polanya Penting

**Pendekatan:** Bar chart harian dengan rolling average 7 hari, bar chart bulanan dengan penanda musim kemarau, stacked bar siang vs malam per bulan, dan time series perbandingan antar tahun.

**Temuan 1: Konsentrasi Musim yang Ekstrem**

Dari 57.785 titik api, **48.710 (84,3%)** terjadi di bulan Juni-Oktober. Puncak tertinggi adalah September: **24.582 titik** hanya dari satu bulan (42,5% dari total keseluruhan). Bulan terendah adalah Desember: hanya 286 titik.

| Bulan | Jumlah | Musim |
|---|---|---|
| Januari | 1.967 | Hujan |
| Februari | 884 | Hujan |
| Maret | 2.670 | Transisi |
| April | 1.047 | Hujan |
| Mei | 1.147 | Transisi |
| Juni | 632 | **Kemarau** |
| Juli | 7.198 | **Kemarau** |
| Agustus | 10.568 | **Kemarau** |
| September | 24.582 | **Kemarau** |
| Oktober | 5.730 | **Kemarau** |
| November | 1.074 | Transisi |
| Desember | 286 | Hujan |

*Apa artinya untuk Problem Statement:* Sumber daya penanganan karhutla (personel, pesawat water bombing, anggaran) tidak perlu didistribusikan merata sepanjang tahun. Alokasi sumber daya yang optimal adalah memusatkan kapasitas pada 3 bulan kritis: Juli, Agustus, September. Sistem FIRELINE harus **secara otomatis menaikkan status siaga** pada awal Juni dan menginformasikan stakeholder jauh sebelum puncak musim.

**Temuan 2: Kebakaran Malam Hari sebagai Sinyal Gambut**

**6.140 titik api (10,6%)** terdeteksi di malam hari. Angka ini tampak kecil, namun signifikansinya sangat besar secara operasional.

Api yang masih aktif terdeteksi satelit di malam hari — padahal embun dan penurunan suhu malam seharusnya meredam api kecil — adalah indikasi kuat **kebakaran gambut bawah permukaan (smoldering peat fire)**. Gambut yang terbakar di bawah tanah tidak terlihat dari atas, menghasilkan asap pekat secara terus-menerus, dan nyaris mustahil dipadamkan hanya dengan siraman air. Kebakaran gambut adalah sumber ISPA yang paling berbahaya karena berhari-hari hingga berminggu-minggu melepaskan partikel PM2.5 ke udara.

Dari 6.140 kebakaran malam, **58,2%** terjadi selama musim kemarau — konsisten dengan pola gambut yang semakin kering dan rentan terbakar saat kemarau. Hanya 52 di antaranya (0,8%) masuk tier Tinggi+Ekstrem dalam hal FRP permukaan, yang berarti kebakaran gambut lebih *tersembunyi* (FRP rendah di permukaan) namun lebih *persisten* (terus menyala sepanjang malam).

*Apa artinya untuk Problem Statement:* Dashboard karhutla konvensional yang hanya menampilkan titik panas dengan FRP tinggi akan **melewatkan ancaman gambut ini**. FIRELINE harus menyertakan filter dan indikator khusus untuk kebakaran malam dengan FRP rendah-menengah yang persisten, karena itu adalah sinyal gambut yang justru paling berbahaya secara jangka panjang.

---

#### Modul B: Spasial dan Keterpaparan Sekolah — Di Mana dan Siapa yang Terancam

**Pendekatan:** Bar chart horizontal terurut per provinsi, histogram jarak ke sekolah dengan kurva CDF (Cumulative Distribution Function) pada sumbu kedua.

**Temuan 3: Ketidakmerataan Beban Kalimantan Barat**

| Provinsi | Titik Api | % Total | Avg Skor Risiko | Max FRP |
|---|---|---|---|---|
| Kalimantan Barat | 36.019 | 62,3% | **78,1** | 652 MW |
| Kalimantan Timur | 9.615 | 16,6% | 61,5 | 550 MW |
| Kalimantan Tengah | 8.481 | 14,7% | 51,6 | **955 MW** |
| Kalimantan Selatan | 3.601 | 6,2% | 63,7 | 826 MW |

*Apa artinya untuk Problem Statement:* Kalimantan Barat bukan hanya paling banyak titik apinya, tetapi juga memiliki rata-rata skor risiko tertinggi (78,1 dari 100) — menunjukkan bahwa kebakaran di Kalimantan Barat secara konsisten berada lebih dekat dengan infrastruktur rentan dan terjadi lebih sering di musim kemarau. Sementara Kalimantan Tengah memiliki titik FRP ekstrem tertinggi (955 MW), menunjukkan bahwa ada kebakaran sangat intens yang butuh penanganan udara (water bombing) di sana meskipun jumlahnya lebih sedikit.

**Temuan 4: 90,7% Titik Api Kritis Mengancam Sekolah dalam 5 km**

Kurva CDF jarak ke sekolah terdekat mengungkapkan temuan yang mengubah paradigma:

| Radius | Jumlah Titik | Kumulatif |
|---|---|---|
| < 1 km | 9.850 | 17,0% |
| < 2 km | 21.800 | 37,7% |
| < 3 km | 32.245 | 55,8% |
| < 5 km | 46.770 | **80,9%** |
| < 10 km | 55.484 | 96,0% |

Median jarak ke sekolah adalah **2,71 km**. Persentil ke-10 adalah 0,96 km. Artinya, 10% titik api berada dalam jarak kurang dari 1 km dari sekolah.

Yang lebih mengejutkan: dari 16.395 titik yang dikategorikan **Kritis**, **14.863 (90,7%)** berada dalam 5 km dari sekolah, dan **11.294 (68,9%)** berada dalam 3 km.

*Interpretasi yang Benar:* Angka 80,9% ini bukan berarti 80% sekolah sedang terbakar. Ini berarti: sebaran sekolah di Kalimantan cukup merata sehingga hampir tidak ada wilayah berpenghuni yang tidak memiliki sekolah dalam radius 5 km. Dengan kata lain, **setiap titik api yang muncul di dekat permukiman hampir pasti mengancam sekolah**.

*Apa artinya untuk Problem Statement:* Jarak ke sekolah adalah proksi yang sangat kuat untuk mengukur "apakah ada manusia yang terancam di sekitar titik api ini". Ini justifikasi ilmiah mengapa Skor Paparan (*Exposure Score*) berbasis jarak sekolah mendapat bobot 40% dalam formula risiko komposit kami. Fitur ini menjadi jembatan antara sinyal satelit mentah (titik koordinat) dengan dampak manusiawi yang konkret (berapa orang, terutama anak-anak, yang terancam).

---

#### Modul C: Intensitas Api (FRP) — Seberapa Parah dan Siapa yang Butuh Penanganan Udara

**Pendekatan:** Histogram skala-log dengan marker persentil, boxplot per provinsi dengan outlier inklusif pada skala logaritmik, donut chart proporsi tier keparahan.

**Temuan 5: Distribusi FRP yang Sangat Timpang (Right-Skewed)**

Statistik deskriptif FRP:

| Statistik | Nilai |
|---|---|
| Minimum | 0,09 MW |
| Median (P50) | **6,27 MW** |
| Rata-rata | 10,81 MW |
| P75 | 11,73 MW |
| P90 | 22,62 MW |
| P95 | **33,63 MW** |
| P99 | 71,51 MW |
| Maksimum | **954,79 MW** |

Rata-rata (10,81 MW) jauh di atas median (6,27 MW). Ini adalah tanda klasik distribusi right-skewed: sebagian kecil nilai ekstrem yang sangat besar menarik rata-rata ke atas. Visualisasi langsung dari histogram linier akan *menyembunyikan* mayoritas data di sisi kiri. Oleh karena itu kami menggunakan skala logaritmik pada sumbu X.

*Apa artinya untuk Problem Statement:* 95% kebakaran (54.895 titik) memiliki FRP di bawah 33,63 MW — ukuran yang masih bisa ditangani oleh tim darat. Hanya **2.890 titik (5%)** yang masuk tier Ekstrem (FRP > P95). Inilah klaster yang **harus menjadi target water bombing dari udara** karena skalanya sudah melampaui kapasitas pemadaman darat. Tanpa analisis distribusi ini, sumber daya udara yang mahal mungkin tersebar tidak efisien.

**Temuan 6: Kalimantan Tengah Menyimpan Api Paling Mematikan**

Meskipun Kalimantan Barat memiliki jumlah titik api terbanyak (62,3%), Kalimantan Tengah memiliki FRP maksimum tertinggi (954,79 MW) — hampir dua kali lipat FRP maksimum Kalimantan Barat (652,45 MW). Boxplot per provinsi dengan outlier inklusif menunjukkan bahwa Kalimantan Tengah memiliki distribusi ekor kanan yang jauh lebih panjang.

*Apa artinya untuk Problem Statement:* Pemimpin operasional yang hanya melihat jumlah titik api per provinsi akan salah mengalokasikan sumber daya water bombing — seharusnya fokus ke Kalimantan Tengah untuk api ekstrem, bukan hanya ke Kalimantan Barat. Ini adalah bukti bahwa **volume titik api dan intensitas titik api adalah dua masalah yang berbeda dan butuh respons berbeda**.

---

#### Modul D: Korelasi Cuaca — Fondasi Sistem Prediktif

**Pendekatan:** Time series dual-axis curah hujan vs jumlah titik api harian, scatter plot bubble dengan ukuran lingkaran mewakili frekuensi (jumlah hari dalam kelompok curah hujan yang sama).

*Catatan teknis penting:* Dataset iklim historis (climate_data.csv) mencakup 2010-2020, sementara data hotspot mencakup 2024-2026. Untuk keperluan analisis korelasi, tanggal iklim digeser 14 tahun ke depan agar overlap dengan periode hotspot. Ini adalah teknik *date-shifting* untuk demonstrasi korelasi musiman (bukan prediksi temporal spesifik).

**Temuan 7: Korelasi Negatif yang Kuat antara Curah Hujan dan Kemunculan Api**

Scatter plot (bubble chart) menunjukkan pola yang jelas: semakin tinggi curah hujan rata-rata (sumbu X), semakin rendah rata-rata titik api harian (sumbu Y). Ukuran bubble besar di sekitar angka curah hujan 0-5 mm menunjukkan bahwa sebagian besar hari-hari di Kalimantan adalah hari yang minim atau tidak ada hujan — dan pada hari-hari inilah kebakaran paling banyak terjadi.

Tren linear negatif pada scatter plot ini memberikan **justifikasi ilmiah untuk sistem peringatan dini prediktif**: jika forecast cuaca menunjukkan curah hujan di bawah ambang tertentu selama 7-14 hari berturut-turut, kemungkinan lonjakan titik api sangat tinggi. Sistem tidak perlu menunggu satelit mendeteksi api — bisa menaikkan siaga **sebelum api muncul**.

*Apa artinya untuk Problem Statement:* Ini adalah temuan yang mengubah FIRELINE dari sekadar *dashboard reaktif* (hanya menampilkan api yang sudah ada) menjadi *platform preventif* (memperingatkan sebelum api terjadi). Dengan mengintegrasikan API forecast BMKG, sistem bisa secara otomatis menginformasikan kepala daerah: "Dalam 10 hari ke depan, curah hujan diperkirakan sangat rendah — aktifkan patroli dini dan siapkan sumber daya pemadaman."

---

### Notebook 04: Indeks Komposit dan Penilaian Risiko

#### Formula Skor Risiko Komposit

Setiap titik api diberi skor 0-100 melalui formula bertingkat:

```
FRP_score = (FRP_capped / FRP_P99) x 100
              dimana FRP_capped = min(FRP, FRP_P99)

exposure_score = max(0, 100 x (1 - jarak_km/50))
              dimana 50 km adalah radius batas pengaruh

base_score = (0.6 x FRP_score) + (0.4 x exposure_score)

pop_multiplier = 0.8 + 0.4 x ((populasi_provinsi - min_pop) / (max_pop - min_pop))
              range: 0.8 (populasi terendah) sampai 1.2 (populasi tertinggi)

season_multiplier = 1.5 jika musim kemarau, 1.0 jika tidak

risk_score = clip(base_score x pop_multiplier x season_multiplier, max=100)
```

**Justifikasi Bobot:**  
- FRP mendapat bobot 60% karena merupakan sinyal fisik langsung tentang seberapa besar dan intens api tersebut — ini adalah penentu utama kapasitas pemadaman yang dibutuhkan.  
- Exposure (jarak sekolah) mendapat bobot 40% karena api yang sama dekat permukiman jauh lebih berbahaya daripada api di hutan terbuka — ini adalah dimensi *dampak manusiawi*.  
- Pengganda musim 1.5x saat kemarau: api di musim kemarau memiliki probabilitas penyebaran yang jauh lebih tinggi karena vegetasi kering, angin, dan ketiadaan hujan yang bisa membantu pemadaman alami.

#### Hasil Penilaian Risiko

| Kategori | Skor | Jumlah | % | Implikasi Respons |
|---|---|---|---|---|
| Rendah | 0-39 | 2.046 | 3,5% | Pantau, tidak perlu respons aktif |
| Sedang | 40-59 | 13.943 | 24,1% | Siapkan tim, pantau berkala |
| Tinggi | 60-79 | 25.401 | 43,9% | Kerahkan tim darat, verifikasi |
| **Kritis** | **80-100** | **16.395** | **28,4%** | **Respons segera, pertimbangkan water bombing** |

- Rata-rata skor: **70,5/100** — situasi secara keseluruhan berada di zona berbahaya
- Median skor: **73,1** — lebih dari separuh titik api memiliki risiko Tinggi atau Kritis
- Dari 16.395 titik Kritis: **90,7%** berada dalam 5 km dari sekolah

---

## Tabel Problem Statement Terintegrasi

Berdasarkan seluruh temuan EDA di atas, berikut adalah sintesis problem statement yang solid:

| # | Problem Statement (Berdasarkan Kondisi Kasus) | Bukti Data dari Analisis | Dampak Jika Tidak Ditangani (Sesuai Deskripsi Kasus) |
|---|---|---|---|
| P1 | **Lonjakan masif titik api pada rentang waktu yang sangat sempit menguras habis kapasitas petugas lapangan** | 84,3% api (48.710 titik) menumpuk hanya di 5 bulan kemarau; puncaknya di September (42,5% dari total). | Personel gabungan yang terbatas kewalahan (overwhelmed); respons selalu terlambat saat puncak krisis. |
| P2 | **Ketiadaan prioritas spasial membuat titik api dekat infrastruktur vital ditangani sama lambatnya dengan api di lahan kosong** | 80,9% titik api mengancam sekolah dalam radius 5 km, dan 90,7% dari total titik api Kritis berdekatan dengan sekolah. | Ribuan siswa dan populasi rentan terpapar kabut asap pekat mematikan tanpa adanya sistem peringatan evakuasi dini. |
| P3 | **Dashboard satelit konvensional gagal memprioritaskan ancaman kebakaran gambut yang membara diam-diam di bawah permukaan** | Terdapat 6.140 titik api malam hari (10,6%) dengan intensitas permukaan (FRP) rendah namun sangat persisten. | Ekosistem lahan gambut terus terbakar tanpa respons prioritas, memicu kabut asap kronis dan lonjakan kasus ISPA. |
| P4 | **Alokasi sumber daya pemadaman mahal tidak proporsional dengan tingkat bahaya aktual di lapangan** | Hanya 5% titik api (2.890) tergolong Ekstrem yang wajib diatasi water bombing; Kalteng menyimpan anomali titik api 955 MW. | Pesawat udara yang terbatas terbuang untuk api kecil, sementara api ekstrem yang sulit dijangkau lewat darat gagal dipadamkan. |
| P5 | **Petugas lapangan bekerja secara buta (blind) akibat fragmentasi data dan overload informasi spasial mentah** | Dari 57.785 titik yang membanjiri layar, nyatanya hanya 1.542 titik (2,7%) yang Kritis sekaligus ber-confidence satelit Tinggi. | Rata-rata waktu verifikasi lapangan membengkak hingga 12-24 jam; api terlanjur menyebar sebelum prioritas ditentukan. |
| P6 | **Absennya sistem peringatan dini prediktif membuat tindakan masyarakat dan command center selalu bersifat pasif & reaktif** | Pola penurunan curah hujan terbukti memicu lonjakan titik api dalam 7-14 hari, namun sinyal iklim ini terisolasi dari data api. | Warga di pelosok kerap baru sadar bahaya saat asap sudah pekat; kehilangan kesempatan krusial untuk pencegahan dini. |
| P7 | **Fragmentasi data spasial menghambat identifikasi area prioritas secara real-time (Actionable Insight)** | Modul `02_data_preparation` membuktikan perlunya penggabungan 4 dataset terpisah (FIRMS, poligon admin, OSM sekolah, cuaca BMKG) untuk akhirnya mengungkap bahwa ada **11.294 titik Kritis berada kurang dari 3 km dari sekolah**. Di sistem yang ada, data ini terpisah. | Petugas rentan salah menetapkan prioritas; titik api kecil di desa padat terabaikan dibanding titik api besar di lahan tak berpenghuni karena ketiadaan konteks. |
| P8 | **Keterlambatan verifikasi lapangan akibat tidak adanya kategorisasi risiko yang otomatis (Working Blind)** | Algoritma `04_composite_risk_index` membuktikan bahwa dari **57.785** titik panas mentah, hanya terdapat **1.542 titik (2,7%)** yang berstatus Kritis sekaligus ber-confidence Tinggi yang paling wajib dicek pertama. | Rata-rata waktu verifikasi lapangan memakan waktu 12-24 jam akibat petugas harus mengecek ribuan titik mentah secara manual tanpa prioritas jelas. |
| P9 | **Ketiadaan sistem informasi peringatan dini berbasis kerentanan paparan (Exposure)** | EDA Modul B menemukan secara empiris bahwa nilai **median jarak titik api ke sekolah adalah 2,71 km**; artinya lebih dari separuh kebakaran memang terjadi persis di zona aktivitas masyarakat rentan. | Warga tak menerima peringatan kontekstual; asap tiba-tiba melumpuhkan aktivitas ekonomi (penutupan bandara) dan warga tak sempat mitigasi mandiri, memicu lonjakan ISPA. |

---

## Usulan Inovasi: FIRELINE AI

### Pergeseran Paradigma: dari Hazard-Centric ke Exposure-Centric

Platform peta titik api yang ada saat ini bersifat *hazard-centric*: mereka menampilkan api. FIRELINE menggeser paradigma ke *exposure-centric*: kami menampilkan **siapa dan apa yang terancam oleh api tersebut**.

### Komponen Solusi

**Komponen 1 — Composite Risk Scoring Engine (Sudah Diimplementasi)**  
Skor Risiko 0-100 yang terotomatisasi untuk setiap titik api, menggabungkan intensitas satelit, kedekatan infrastruktur, populasi, dan faktor iklim. Mengubah 57.785 titik acak menjadi daftar terurut "10 titik yang paling butuh respons sekarang".

**Komponen 2 — Predictive Alert System (Berbasis Temuan Modul D)**  
Integrasi API forecast BMKG: jika prakiraan curah hujan < 5mm selama 7 hari berturut-turut, sistem secara otomatis mengirimkan notifikasi ke kepala daerah, menaikkan status siaga di dashboard, dan merekomendasikan aktivasi patroli dini. Sistem ini *mencegah* sebelum api muncul.

**Komponen 3 — School Zone Alert (Berbasis Temuan Modul B)**  
Setiap titik api Kritis yang muncul dalam radius 3 km dari sekolah memicu alert otomatis ke Dinas Pendidikan setempat. Dashboard menampilkan berapa sekolah dalam zona bahaya, dengan rekomendasi tindakan (penutupan sementara, distribusi masker).

**Komponen 4 — Respons Routing Engine (Berbasis Temuan Modul C)**  
Titik api Ekstrem (FRP > P95) secara otomatis di-flag untuk respons udara (water bombing). Titik api Tinggi dan Kritis di-routing ke tim darat terdekat. Titik Rendah/Sedang masuk antrian pantauan. Ini mengoptimalkan penggunaan sumber daya yang terbatas.

### Inovasi vs Platform yang Ada

| Aspek | Platform Konvensional | FIRELINE AI |
|---|---|---|
| Pendekatan | Tampilkan semua titik api | Filter dan prioritaskan berdasarkan risiko terintegrasi |
| Ukuran bahaya | Hanya FRP atau jumlah titik | FRP + kedekatan infrastruktur + populasi + musim |
| Waktu respons | Reaktif setelah satelit deteksi | Preventif berdasarkan forecast cuaca |
| Kelompok rentan | Tidak diperhitungkan | Sekolah dan kepadatan permukiman (populasi) diintegrasikan |
| Output | Peta titik | Daftar prioritas + routing respons + alert otomatis |

---

## Keterbatasan dan Langkah Pengembangan Selanjutnya

**Keterbatasan yang Disadari:**

1. **Hotspot bukan kebakaran terverifikasi** — deteksi satelit bisa menghasilkan false positive (panas industri, jalan aspal panas, dll). Confidence tinggi (`h`) dari NASA hanya 2.272 dari 57.785 titik (3,9%). Skor risiko harus diperkuat dengan verifikasi lapangan atau cross-check dengan data ESA WorldCover.

2. **Data iklim tidak overlap langsung** — climate_data.csv berakhir 2020, sedangkan hotspot adalah 2024-2026. Date-shifting dilakukan untuk demonstrasi korelasi, bukan untuk prediksi temporal presisi.

3. **Kalimantan Utara tidak terwakili** — data provinsi tidak memiliki batas Kalimantan Utara yang terpisah, sehingga seluruh analisis provinsi hanya mencakup 4 dari 5 provinsi Kalimantan.

4. **Data gambut belum terintegrasi** — kebakaran gambut memiliki karakteristik sangat berbeda (FRP rendah, durasi panjang, asap tebal). Integrasi peta gambut Indonesia akan meningkatkan akurasi skor risiko secara signifikan.

**Pengembangan Selanjutnya:**

- Integrasi data lahan gambut (BRG - Badan Restorasi Gambut) sebagai lapisan risiko tambahan
- Model machine learning untuk prediksi kemunculan api berbasis forecast cuaca (Random Forest atau XGBoost dengan fitur lag curah hujan 7-14 hari)
- Integrasi API BMKG real-time untuk komponen Predictive Alert System
- Data kependudukan grid (BPS) yang lebih halus untuk menggantikan proksi populasi provinsi
