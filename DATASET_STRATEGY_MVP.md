# Strategi Dataset FIRELINE untuk MVP dan Case Study

**Gate audit terbaru:** kesamaan periode belum berarti penyelarasan hari.
FIRMS memakai UTC, sedangkan cache POWER memakai LST. Sebelum korelasi
dipakai sebagai bukti, selaraskan jendela waktu, tinjau mask daratan lima
provinsi (rata-rata regional saat ini masih berbasis bounding box), lalu
hitung ulang dan uji pengaruh musim. Cuaca tetap di luar skor prioritas.

## Keputusan utama

Dataset utama tetap **NASA FIRMS VIIRS NOAA-20 2024–2026**. Seluruh angka dasar tentang observasi anomali panas, waktu, lokasi, intensitas radiasi (`frp`), serta kualitas deteksi berasal dari dataset ini. Dataset eksternal hanya menambah konteks; dataset eksternal tidak boleh menggantikan FIRMS sebagai sumber utama dan tidak boleh dipakai untuk mengubah observasi satelit menjadi klaim kebakaran terverifikasi.

Tujuan MVP adalah **memetakan dan memprioritaskan area yang perlu diverifikasi**, bukan memprediksi kebakaran, memastikan sekolah terdampak, atau mengotomatisasi keputusan tanggap darurat.

Unit analisis produk yang disepakati adalah `grid_id + date`:

- `grid_id` merangkum observasi berdekatan ke area sekitar 0,1 derajat;
- `date` menjaga antrean tetap dapat difilter menurut waktu;
- beberapa observasi satelit pada area dan hari yang sama diringkas menjadi satu kandidat area verifikasi.

## Posisi setiap sumber data

| Dataset | Peran pada MVP | Keputusan | Batas interpretasi |
|---|---|---|---|
| NASA FIRMS VIIRS NOAA-20 2024–2026 | Acuan utama untuk pola waktu, lokasi, FRP, dan kualitas observasi | **Wajib / baseline** | Menunjukkan anomali panas yang terdeteksi satelit, bukan kebakaran lapangan yang sudah dikonfirmasi |
| Batas provinsi Indonesia (GeoJSON) | Memberi label wilayah untuk filter dan ringkasan dashboard | **Dipakai dengan audit cakupan** | Area tanpa label harus ditandai `Data Terbatas`, bukan dibuang diam-diam |
| Indonesia School Dataset | Konteks awal kedekatan fasilitas publik | **Dipakai sebagai konteks paparan** | Jarak dekat tidak membuktikan sekolah terbakar atau warga terdampak; tidak boleh menjadi validasi bagi skor yang juga memakai jarak sekolah |
| NASA POWER Daily | Hujan, suhu, kelembapan, dan angin pada periode yang sejajar dengan FIRMS | **Eksperimen eksternal pertama** | Resolusinya lebih kasar daripada grid produk; hubungan statistik bersifat eksploratif, bukan sebab-akibat atau forecast tervalidasi |
| BMKG prakiraan cuaca terbuka | Kandidat konteks operasional untuk kondisi mendatang | **Pasca-MVP / konseptual** | Feed prakiraan singkat, bukan pengganti data historis untuk pelatihan model |
| ERA5-Land | Kandidat cuaca historis beresolusi lebih rapat | **Cadangan bila NASA POWER terlalu kasar** | Unduhan dan pengolahan lebih berat; belum diperlukan untuk membuktikan MVP checkpoint awal |
| ESA WorldCover | Kandidat kelas tutupan lahan | **Opsional setelah validasi** | Tutupan lahan bukan label gambut dan tidak membuktikan tipe kebakaran |
| Pontianak Weather Daily 2021–2024 | Pembanding lokal untuk satu kota | **Tidak dijadikan representasi seluruh Kalimantan** | Satu kota tidak cukup untuk menjelaskan variasi cuaca seluruh pulau dan periodenya hanya overlap sebagian |
| Indonesia Climate 2010–2020 | Referensi klimatologi lama | **Tidak di-join sebagai cuaca aktual 2024–2026** | Tahun tidak boleh digeser agar tampak sejajar dengan FIRMS |
| Forest Fires Dataset (Portugal) | Dataset latihan dari konteks wilayah lain | **Dikeluarkan dari MVP** | Geografi, iklim, dan definisi target tidak sebanding dengan case study Kalimantan |

## Urutan pekerjaan

1. Pertahankan seluruh EDA Kaka sebagai audit baseline FIRMS.
2. Gunakan notebook integrasi v2 hanya untuk pembentukan `grid_id + date`, ringkasan fitur, dan antrean prioritas provisional.
3. Validasi NASA POWER pada periode FIRMS yang sama tanpa manipulasi tahun.
4. Ukur kelengkapan join dan hubungan eksploratif cuaca terhadap jumlah observasi FIRMS pada jeda 0, 1, 3, 7, dan 14 hari.
5. Pertahankan skor prioritas sebagai **provisional** sampai bobotnya divalidasi oleh mentor/domain expert.
6. Berikan hasil agregat kepada PMA untuk narasi masalah, UX untuk informasi dan status pada wireframe, serta SEA untuk rancangan kontrak data konseptual. SEA tidak diwajibkan membangun API nyata pada MVP ini.

## Aturan klaim untuk PRD dan presentasi

### Boleh disebut sebagai fakta data

- jumlah dan rentang waktu observasi FIRMS;
- pola musiman, distribusi FRP, confidence, dan day/night setelah dihitung ulang;
- jumlah unit `grid_id + date` dan kelengkapan label wilayah;
- median atau persentase jarak ke sekolah, disertai batas interpretasinya;
- kualitas dan kelengkapan hasil join dataset eksternal.

### Harus disebut sebagai asumsi yang perlu divalidasi

- area prioritas dapat mempercepat verifikasi petugas;
- variabel cuaca dapat meningkatkan prioritas area;
- informasi fasilitas publik berguna bagi keputusan operator;
- ambang dan bobot skor sesuai kebutuhan lapangan.

### Tidak boleh disebut sebagai fakta dari data saat ini

- sistem memprediksi kebakaran;
- observasi FIRMS adalah kebakaran terverifikasi;
- sekolah atau warga pasti terdampak karena berada dekat observasi;
- penurunan hujan menyebabkan lonjakan pada jeda tertentu tanpa evaluasi model yang benar;
- waktu verifikasi 12–24 jam atau keterlambatan komunikasi sebagai hasil EDA, kecuali ada sumber riset pengguna/operasional terpisah.

## Sumber resmi

- NASA FIRMS VIIRS Fire Hotspots: https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html
- NASA POWER Daily API: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- BMKG Data Terbuka: https://data.bmkg.go.id/
- ERA5-Land: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land
- ESA WorldCover: https://esa-worldcover.org/en/data-access
