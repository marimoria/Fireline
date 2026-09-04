# Status review publikasi Checkpoint 2

Paket ini menyimpan output eksperimen yang sudah ada, bukan hasil eksekusi ulang.
Kode dan output cuaca dipertahankan untuk review, bukan sebagai hasil final.

## Batas yang harus dibaca bersama notebook dan gambar

- FIRMS memakai tanggal UTC; header cache NASA POWER memakai LST. Join berdasarkan
  label tanggal belum menyamakan jendela 24 jam. Angka kelengkapan 100% hanya
  menunjukkan ketersediaan nilai pada label tanggal yang dicocokkan.
- Korelasi, analisis lag, dan panel cuaca dashboard masih sebelum perbaikan tersebut.
  Jangan kutip angka korelasi sebagai supporting fact PRD atau hasil prediksi.
- Rata-rata regional cuaca memakai bounding box, bukan mask daratan lima provinsi.
  Laut dan wilayah di luar cakupan Indonesia dapat memengaruhi ringkasannya.
- Skor prioritas hanya memakai aktivitas, persistensi, dan FRP: tidak memakai
  cuaca/sekolah. Bobot dan label P1 tetap heuristik yang perlu validasi manusia.
- Median sekolah 2,94 km dihitung atas baris grid-hari, bukan sekali per grid unik.
  Kedekatan ini bukan bukti sekolah atau warga terdampak.
- Data 2024 dan 2026 parsial. Persentase bulanan seluruh periode tidak membuktikan
  pola musim berulang atau kapasitas petugas yang kewalahan.
- Gambar dashboard adalah rancangan historis, bukan feed live atau alat operasional.

## Review berikutnya

1. Tentukan standar waktu harian yang konsisten dan ambil/agregasikan cuaca sesuai.
2. Tinjau domain spasial, definisi hari tanpa deteksi, dan pengaruh musim.
3. Hitung ulang korelasi, lag, serta panel cuaca; dokumentasikan perubahan hasil.
4. Validasi bobot prioritas dan kegunaan antrean dengan mentor serta calon pengguna.

## Isi branch

Dua notebook .ipynb, dokumentasi, dua ringkasan JSON, requirements, dan low-fi PNG.
Tidak ada CSV, versi .py, cache NASA POWER/BIG, lingkungan Python, hasil regenerasi
EDA Kaka, atau naskah mentoring pribadi. Data lokal tetap diperlukan untuk
menjalankan ulang; lihat data/README.md. Jangan menganggap output lama berubah
hanya karena peringatan review ditambahkan.
