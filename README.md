# FIRELINE DSA Integrated 

`FIRELINE_DSA_Integrated_Baseline_v2.ipynb` adalah baseline analisis Data Science Academy untuk Checkpoint 1 FIRELINE. Notebook ini menerjemahkan observasi anomali panas satelit menjadi daftar area yang dapat **diprioritaskan untuk verifikasi manusia** oleh BPBD, command center, atau koordinator relawan.

Outputnya bukan prediksi kebakaran, bukan status bahaya resmi, dan bukan rekomendasi tindakan darurat otomatis. Istilah P1, P2, dan P3 hanya menunjukkan urutan verifikasi dalam prototipe.

## Pertanyaan yang dijawab

Notebook membantu tim membaca empat hal:

1. Kapan dan di mana observasi anomali panas terkonsentrasi?
2. Area mana yang aktif atau berulang dalam tujuh hari terakhir?
3. Area mana yang relatif lebih relevan untuk diverifikasi lebih dahulu berdasarkan aktivitas, persistensi, FRP, dan kedekatan sekolah?
4. Informasi dan batasan apa yang perlu ditampilkan kepada operator agar skor tidak disalahartikan?

Unit analisis akhirnya adalah **grid 0,1 derajat per tanggal**, dengan primary key `(grid_id, date)`. Satu baris bukan satu kejadian kebakaran; satu baris adalah ringkasan observasi satelit pada satu area dan satu tanggal.

## Cara membaca notebook

### 1. Kontrak analisis dan guardrail

Bagian awal menetapkan arti unit data, pengguna, keluaran, dan batas klaim. Bagian ini sebaiknya dibaca sebelum melihat skor karena menjelaskan bahwa `confidence` merupakan konteks kualitas observasi, bukan probabilitas terjadinya kebakaran.

### 2. Audit dataset

Bagian audit mencatat sumber yang benar-benar digunakan, jumlah baris, fungsi setiap dataset, serta keterbatasannya. Dataset utama berisi 61.583 observasi FIRMS. Dataset sekolah dan batas provinsi hanya memberikan konteks spasial sementara.

### 3. Pembersihan dan EDA

Pembersihan mempertahankan semua baris yang memenuhi validitas dasar tanggal, koordinat, dan FRP. Grafik harian dan bulanan dipakai untuk membaca pola observasi, dengan pemisahan per tahun karena 2024 dan 2026 memiliki cakupan tahun yang tidak lengkap.

FRP dibaca sebagai intensitas radiasi pada observasi satelit. Nilai ini tidak boleh langsung diterjemahkan menjadi luas kebakaran atau kebutuhan water bombing.

### 4. Feature engineering

Observasi diringkas menjadi fitur berikut:

| Fitur | Makna dalam notebook |
|---|---|
| `detection_count` | Jumlah observasi pada grid dan tanggal tersebut |
| `detections_7d` | Total observasi pada grid selama tujuh hari berjalan |
| `active_days_7d` | Banyaknya hari aktif dalam jendela tujuh hari |
| `frp_median_mw` | Median FRP agar tidak terlalu dipengaruhi nilai ekstrem |
| `nearest_school_distance_km` | Jarak ke sekolah terdekat sebagai proksi exposure sementara |
| `confidence` share | Konteks kualitas observasi satelit |
| `night_share` | Konteks waktu observasi, bukan bukti kebakaran gambut |

### 5. Skor prioritas verifikasi

Skor provisional terdiri dari aktivitas 35%, persistensi tujuh hari 30%, FRP 20%, dan kedekatan sekolah 15%. Bobot tersebut belum dianggap final dan masih memerlukan validasi dengan calon pengguna serta mentor.

- **P1 — Verifikasi segera:** kelompok skor tertinggi dalam prototipe.
- **P2 — Pantau ketat:** kelompok prioritas menengah.
- **P3 — Pemantauan biasa:** tetap ditampilkan, tetapi berada di bawah P1 dan P2.
- **DATA TERBATAS:** label kualitas ketika konteks spasial atau kualitas observasi belum memadai.

`primary_reason` menunjukkan komponen yang paling kuat pada suatu baris. Kolom ini membantu operator memahami alasan urutan tanpa menganggap skor sebagai keputusan otomatis.

### 6. Low-fidelity dashboard

Dashboard di akhir notebook adalah wireframe berbasis data. Fokusnya bukan estetika final, melainkan hierarki informasi:

- filter tanggal, provinsi, dan level prioritas;
- KPI jumlah grid aktif, antrean P1, jumlah observasi, dan data terbatas;
- peta prioritas verifikasi;
- antrean area yang perlu dilihat lebih dahulu;
- tren observasi historis;
- panel alasan prioritas dan guardrail.

UX dapat menggunakan susunan ini sebagai dasar desain Figma. SEA dapat menggunakan nama field dan primary key sebagai awal kontrak data. PMA dapat menggunakan temuan serta guardrail untuk memperjelas scope PRD.

## Dataset

Dataset yang digunakan:

1. NASA FIRMS VIIRS NOAA-20 sebagai sumber observasi anomali panas.
2. Indonesia School Dataset sebagai proksi awal fasilitas sensitif.
3. Indonesia Province GeoJSON untuk label dan ringkasan wilayah.

Dataset cuaca historis tidak dipaksakan masuk ke scoring karena periode dan cakupan spasialnya belum selaras. Tidak ada pergeseran tanggal untuk membuat korelasi semu. Integrasi cuaca aktual atau forecast baru relevan ketika tim benar-benar mengembangkan fungsi predictive atau early warning.

## Batas interpretasi

- Deteksi satelit belum tentu kebakaran terverifikasi.
- Banyak observasi tidak sama dengan banyak kejadian kebakaran unik.
- `confidence` FIRMS bukan probabilitas kebakaran.
- P1/P2/P3 bukan tingkat bahaya resmi.
- Kedekatan sekolah bukan bukti bahwa sekolah atau penduduk sudah terdampak.
- Observasi malam tidak cukup untuk menyimpulkan kebakaran gambut.
- GeoJSON provinsi masih memakai batas lama dan belum memisahkan Kalimantan Utara secara andal.
- Tahun 2024 dimulai pada Agustus dan 2026 berakhir pada Mei, sehingga total tahun tidak boleh dibandingkan langsung.


