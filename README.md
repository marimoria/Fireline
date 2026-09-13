# FIRELINE — Peta Prioritas Pemantauan

Prototipe DSA untuk **fitur 02 / Mapping**, mengikuti batas lingkup keputusan PMA/UX pasca-Checkpoint 2. Paket ini mengubah observasi satelit menjadi peta area, daftar Top 10, dan alasan skor yang dapat dibaca pengguna nonteknis.

**Status: versi lokal untuk review, bukan layanan operasional.** Data historis 1 Agustus 2024–31 Mei 2026. Tidak ada prediksi kebakaran, pengiriman notifikasi, validasi otomatis laporan warga, atau penugasan relawan.

## Mulai membaca

- **Dashboard:** buka `review_outputs/FIRELINE_Priority_Map.html` yang sudah dibangun di komputer kerja. Filter, daftar, dan detail berada dalam satu berkas; pustaka peta serta peta dasar memerlukan internet.
- **Notebook 05 — Dataset Scope Audit:** menjelaskan satuan data, pemeriksaan waktu/koordinat, penyaringan lima provinsi, dan mengapa jumlah data berbeda dari versi lama.
- **Notebook 06 — MVP Priority Map:** menjelaskan pembentukan area-hari, aktivitas, persistensi, FRP, kontribusi skor, uji sensitivitas, konteks sekolah, dan pembuatan dashboard.
- **[Laporan review](REVIEW_REPORT.md):** hasil penting, perbedaan versi, dan keputusan yang masih perlu ditinjau PMA/UX.
- **[Definisi data dan skor](DATA_CONTRACT.md):** acuan penyamaan istilah serta aturan perhitungan.

Dashboard membuka 3 September 2024 karena observasinya paling banyak dalam hasil penyaringan, **bukan karena itu kondisi terkini**. Pilih tanggal dan provinsi; angka ringkasan dan Top 10 mengikuti filter. Klik nomor peta atau baris daftar untuk melihat alasan prioritas. Nama kabupaten dapat berulang karena peringkat diberikan kepada area-grid, bukan kabupaten.

## Temuan yang menjadi acuan versi ini

| Tahap | Jumlah | Cara membacanya |
|---|---:|---|
| Berkas utama mentah | 61.583 | Baris observasi, bukan jumlah kebakaran unik |
| Cocok dengan poligon BIG lima provinsi Kalimantan | 60.708 | Termasuk Kalimantan Utara |
| Tidak cocok dengan poligon tersebut | 875 | Disimpan terpisah untuk audit, tidak otomatis berarti koordinat salah |
| Area-grid unik | 2.846 | Kotak koordinat 0,1°; unit pengelompokan, bukan luas terbakar |
| Kombinasi area-tanggal | 26.773 | Satu baris per grid dan tanggal UTC |

Pada 3 September 2024 terdapat 2.399 observasi yang dikelompokkan menjadi 505 area. Angka ini mendukung kebutuhan peringkasan informasi; **tidak membuktikan petugas kewalahan atau verifikasi memakan waktu 12–24 jam**.

## Apa arti skor?

Skor sementara menggabungkan aktivitas 40%, hari aktif dalam tujuh hari 35%, dan FRP median relatif 25%. Aktivitas dan FRP dibandingkan dengan seluruh area aktif Kalimantan pada tanggal yang sama. Filter provinsi tidak menghitung ulang skor.

P1 ≥80, P2 60–<80, P3 <60 adalah batas aturan prototipe, bukan kategori bahaya yang tervalidasi. P3 **bukan aman**. Skor bukan probabilitas kebakaran, confidence satelit, tingkat kerusakan, atau perintah respons. Bobot belum dinyatakan optimal; notebook menyertakan variasi bobot dan penghilangan komponen.

Sekolah hanya konteks fasilitas. Jarak dihitung dari observasi representatif ke sekolah terdekat yang tersedia, bukan dari pengguna dan bukan radius dampak. Cuaca, populasi, serta laporan warga tidak dimasukkan ke skor ini.

## Asal dan keterulangan

Dataset utama tetap berkas FIRMS yang diberikan dalam proyek. BIG dipakai untuk penyaringan geografis; dataset sekolah untuk konteks. Geometri kab/kota diambil dari HTML Kaka, **tanpa memakai skor atau ranking lamanya**. Sumber/tahun asli geometri kab/kota masih perlu dilengkapi; jika HTML tidak tersedia, aplikasi menggunakan poligon provinsi BIG.

Nama, ukuran, dan SHA-256 setiap masukan tercatat dalam `review_outputs/audit_summary.json`. CSV, konfigurasi lokasi berkas, dan payload dashboard tetap lokal. Berkas HTML mengandung data lokasi; periksa dahulu sebelum membagikannya.

Referensi: [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/active_fire/), [BIG batas provinsi](https://geoservices.big.go.id/gis/rest/services/STIG/Batas_Provinsi/MapServer), [dataset sekolah](https://www.kaggle.com/datasets/marchotridyo/indonesia-school-dataset-with-province-data).

## Menjalankan ulang (opsional)

Gunakan Python 3.12 dan `requirements.txt`. Salin `config.example.json` menjadi `config.local.json`, lalu isi lokasi berkas lokal. Jalur relatif dibaca dari folder konfigurasi. Tidak ada unduhan dataset otomatis.

```powershell
python -m pip install -r requirements.txt
python -m fireline.pipeline
python -m pytest -q
python -m streamlit run dashboard.py --server.address 127.0.0.1
```

Notebook 05 lalu 06 dapat dijalankan melalui Jupyter dengan lingkungan yang sama. Versi HTML juga bisa dibuka langsung tanpa Streamlit. Saat pustaka peta gagal dimuat, daftar dan detail tetap tersedia.

## Hubungan dengan pekerjaan sebelumnya

Paket dimulai dari `main` commit `5a962314d4d370b3daf505cdfaf6f1b50ed23903`, kemudian dikembangkan di branch lokal `checkpoint3-dsa-priority-map`. Notebook dan dashboard Maria dipertahankan dalam `legacy/` sebagai arsip, bukan sumber angka resmi versi ini. Notebook v2 Evan dan HTML Kaka menjadi referensi konsep; paket ini bukan salinan hasil skornya.

Notebook 05 dan 06 adalah notebook aktif. Modul `fireline/` adalah implementasi yang dipakai bersama keduanya, bukan duplikat notebook `.py`. Tidak ada push otomatis.
