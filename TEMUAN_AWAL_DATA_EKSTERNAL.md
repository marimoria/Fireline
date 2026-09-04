# Temuan Awal Dataset Eksternal FIRELINE — status review

NASA FIRMS tetap acuan utama. NASA POWER dipilih sebagai eksperimen cuaca karena
menyediakan periode historis yang sama tanpa menggeser tahun dataset lama.

## Yang sudah diperiksa pada output sebelumnya

| Pemeriksaan | Hasil | Batas makna |
|---|---|---|
| FIRMS | 61.583 observasi, 1 Agustus 2024–31 Mei 2026 | Deteksi anomali panas, bukan kebakaran terverifikasi |
| Label tanggal | 669 hari | Tahun 2024 dan 2026 parsial; hari tanpa deteksi bukan bukti tidak ada kebakaran |
| Node POWER | 342 | Resolusi lebih kasar daripada grid produk |
| Kelengkapan empat variabel | 100% pada label tanggal yang dicocokkan | Bukan bukti jendela 24 jam sudah sama |
| Duplikat node-tanggal | 0 setelah normalisasi | Hasil pembersihan overlap, bukan validasi akurasi cuaca |

## Temuan audit yang mengubah interpretasi

FIRMS memakai UTC, sedangkan cache POWER berheader LST. Join berdasarkan tanggal
yang sama belum menyamakan periode harian. Selain itu, rata-rata cuaca regional
memakai bounding box, belum mask daratan lima provinsi. Karena itu, korelasi
dan analisis jeda yang tersimpan di notebook belum menjadi angka resmi PRD.
Output tersebut belum dihitung ulang; grafik lama dipertahankan untuk review.

Langkah berikutnya adalah menyelaraskan waktu, meninjau domain spasial, lalu
mengulang korelasi dan menguji pengaruh musim. Jangan menyimpulkan kemampuan
prediksi 7–14 hari dari eksperimen lama.

## Keputusan MVP

- Skor hanya memakai aktivitas FIRMS, persistensi, dan FRP.
- Cuaca tidak masuk skor; panel cuaca pada low-fi masih contoh sebelum koreksi.
- BIG memberi label provinsi dengan status data terbatas untuk baris tidak cocok.
- Sekolah hanya konteks kedekatan, bukan bukti dampak atau validasi skor.
- Tidak ada klaim sebab-akibat, kebakaran terverifikasi, atau keputusan respons otomatis.

## Artefak terkait

- [Notebook eksperimen](notebooks/02_FIRELINE_External_Data_Validation.ipynb).
- [Strategi dataset](DATASET_STRATEGY_MVP.md).
- [Status review lengkap](REVIEW_STATUS.md).
- Grafik/tabel ekspor dan cache tetap lokal, tidak masuk branch ini.
