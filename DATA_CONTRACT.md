# Definisi Data dan Skor — priority-map-1.0

## Ruang lingkup dan satuan

1. Satu observasi adalah satu baris deteksi satelit. Deteksi berdekatan atau berulang tidak otomatis menjadi kejadian kebakaran berbeda.
2. Koordinat menggunakan lintang/bujur derajat EPSG:4326. Lintang menunjukkan posisi utara–selatan; bujur timur–barat.
3. Waktu observasi dibentuk dari `acq_date` + `acq_time` HHMM dalam UTC. Tampilan lokal mengikuti WIB atau WITA. Waktu pembuatan dashboard bukan waktu deteksi satelit.
4. Hapus duplikat seluruh kolom sumber, periksa koordinat dan HHMM, pertahankan `type=0`, kemudian cocokkan titik dengan lima poligon provinsi BIG (kode 61–65). Titik batas ganda diberi label deterministik dan ditandai, tidak digandakan.
5. FRP tidak valid menjadi nilai kosong dan dicatat; observasi tersebut tidak dihapus. Confidence l/n/h tetap ditampilkan sebagai konteks kualitas deteksi, bukan probabilitas kebenaran laporan warga.
6. Grid memakai `floor(latitude/0.1):floor(longitude/0.1)` dengan toleransi numerik 1e-9. Kunci unik keluaran adalah `grid_id + date` (UTC). Grid kurang lebih 11 km per sisi di sekitar khatulistiwa; ini bukan ukuran kebakaran.

## Kolom utama area-hari

| Kolom | Definisi |
|---|---|
| `detection_count` | Jumlah observasi yang lolos audit dalam grid pada tanggal tersebut |
| `active_days_7d` | Jumlah tanggal berbeda dengan deteksi, dari D−6 sampai D; bukan bukti api terus menyala |
| `detections_7d` | Total observasi D−6 sampai D, hanya informasi pendamping, bukan komponen persistensi |
| `frp_median_mw`, `frp_max_mw` | Median/maksimum FRP valid dalam grid-hari; tidak mengukur luas atau tingkat kerusakan |
| `latitude`, `longitude` | Koordinat observasi dengan FRP tertinggi; seri dipilih berdasarkan waktu terbaru lalu nomor baris sumber |
| `province_name` | Provinsi observasi representatif; grid yang memuat lebih dari satu provinsi diberi catatan |
| `region_name` | Kab/kota observasi representatif berdasarkan geometri tampilan; dapat tidak tersedia |
| `nearest_school_km` | Jarak haversine (radius bumi 6371,0088 km) dari observasi representatif ke sekolah terdekat dalam referensi |
| `last_seen_utc` | Waktu observasi paling akhir di grid-hari; tidak selalu waktu titik representatif |
| `quality_note` | Jendela awal <7 hari, FRP kosong, confidence tidak dikenal, lintas provinsi, atau sekolah tidak tersedia |

Karena grid lintas provinsi mengikuti titik representatif, jumlah observasi per provinsi pada dashboard tidak selalu identik dengan audit provinsi per titik. Total Kalimantan tetap sama. Poligon kab/kota menampilkan rata-rata skor **grid yang terpilih**, bukan skor kabupaten resmi dan bukan rata-rata berbobot luas/populasi.

## Formula yang dapat diperiksa

```text
A = mid-rank percentile(jumlah deteksi grid pada D)
P = hari aktif pada [D−6, D] / 7
F = mid-rank percentile(FRP median grid pada D)
skor = 40*A + 35*P + 25*F
```

Persentil dihitung per tanggal terhadap seluruh area aktif Kalimantan: `(rank_rata_rata − 0,5) / jumlah_nilai_valid`. Nilai nol mendapat 0. Nilai kosong mendapat kontribusi 0 dan catatan kualitas; ini asumsi konservatif penghitungan, bukan bukti aman. Bila semua nilai positif sama, masing-masing mendapat 0,5, termasuk hari dengan satu area.

Skor disimpan empat desimal; P1 ≥80, P2 ≥60 dan <80, P3 <60. Daftar diurutkan skor menurun lalu `grid_id` secara leksikografis. Nomor peta dan daftar berasal dari hasil filter yang sama. Nilai yang terlihat dibulatkan; kategori memakai skor tersimpan.

Skor bersifat relatif **antararea pada tanggal sama**. Angka pada dua tanggal dengan kelompok pembanding berbeda tidak boleh dianggap perubahan bahaya absolut. Hari tanpa deteksi tidak menghasilkan baris area; bukan bukti sensor memantau penuh atau api tidak ada. Enam hari pertama memiliki riwayat yang belum lengkap dan ditandai, tetapi belum diberi penyesuaian bobot.

## Uji sensitivitas bukan uji akurasi

Bandingkan anggota Top 10 baseline dengan tiga variasi bobot dan tiga penghilangan komponen (bobot tersisa dinormalisasi). Jaccard = anggota bersama / gabungan anggota. Hanya hari dengan >10 area disertakan, agar hasil bukan otomatis 1. Ada 362 hari informatif pada snapshot ini. Label lapangan belum tersedia; tidak dihitung precision, recall, waktu respons, atau pengurangan kerugian.

## Batas integrasi

Ini kontrak keluaran analitik, **bukan API produksi**. Dataset historis tidak memverifikasi aduan warga saat ini. Geolokasi pengguna, jarak pengguna, notifikasi, identitas, dan proses validasi manusia tidak dijalankan di paket ini. Jika UI produk meminta jarak dari posisi warga, jangan mengganti maknanya dengan jarak sekolah; perlu spesifikasi terpisah PMA/UX.
