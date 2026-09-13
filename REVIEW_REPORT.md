# Laporan Review Lokal FIRELINE

Tanggal: 13 September 2026. Status: implementasi prototipe fitur Mapping selesai dan sudah dipush ke branch `checkpoint3`; belum produk operasional.

## Yang sudah dikerjakan

- Audit dataset utama secara per-observasi terhadap batas lima provinsi BIG.
- Dua notebook aktif yang berhasil dijalankan ulang, dengan tabel dan visualisasi hasil.
- Dashboard HTML interaktif dan pembungkus Streamlit lokal: tanggal, provinsi, tingkat prioritas, Top 10, marker, heatmap, poligon kab/kota, rincian kontribusi, dan aktivitas tujuh hari.
- Dashboard Tableau dipublikasikan untuk review: [FIRELINE Priority Dashboard](https://prod-apsoutheast-c.online.tableau.com/t/evanluis198-ff55726322/views/dsa/FIRELINEPriorityDashboard). Isinya peta hotspot, tren bulanan, Top 10, serta filter provinsi, bulan observasi, dan tingkat prioritas.
- Tooltip marker Tableau menampilkan area/grid, prioritas, skor, jumlah observasi, hari aktif 7 hari, FRP median, koordinat, sekolah terdekat dan jarak, waktu observasi terakhir, sumber, serta caveat luas terdampak belum tersedia. HTML memberi detail yang lebih lengkap dalam panel setelah marker atau baris Top 10 dipilih; perbedaan ini dicatat sebagai batas format Tableau, bukan perbedaan sumber atau skor.
- Dokumentasi definisi data, formula, batas interpretasi, sumber, dan pengujian.
- Arsip Maria dipertahankan di `legacy/`; notebook sumber Kaka untuk HTML tidak ditemukan sehingga proses dibuat ulang, bukan mengklaim mereproduksi notebook Kaka.

Paket hanya menangani kebutuhan DSA fitur 02. Grafik tujuh hari dan rincian kontribusi merupakan penjelasan analitik dalam prototipe, bukan tambahan modul produk.

## Temuan yang aman dijelaskan ke tim

**Pertama, nama berkas tidak cukup untuk menjamin cakupan.** Dari 61.583 observasi, 60.708 cocok dengan batas lima provinsi Kalimantan. Sebanyak 875 tidak cocok dan tetap disimpan terpisah. Penyebab seluruh baris tersebut belum diklasifikasikan; jangan menyebut semuanya Sulawesi atau koordinat salah tanpa audit lanjutan.

**Kedua, Kalimantan Utara ada.** Hasil per titik: Kalbar 36.019, Kaltim 10.191, Kalteng 8.478, Kalsel 3.583, Kaltara 2.437. Angka ini menggambarkan komposisi berkas pada periode terbatas, bukan peluang kebakaran per wilayah. Perbandingan tersebut belum dinormalisasi luas wilayah, lintasan satelit, atau tutupan awan.

**Ketiga, jumlah deteksi berbeda dari persistensi.** Sepuluh deteksi pada satu hari adalah aktivitas yang banyak, tetapi hanya satu hari aktif. Definisi baru memisahkan keduanya agar persistensi tidak sekadar mengulang hitungan deteksi. Ini koreksi terhadap rancangan baseline lama, bukan perubahan kosmetik bobot.

**Keempat, peringkasan membantu membaca kumpulan observasi.** Pada 3 September 2024, 2.399 observasi menjadi 505 area-hari; satu area berstatus P1 menurut aturan sementara. Ini tidak berarti hanya satu kebakaran berbahaya dan tidak membuktikan waktu verifikasi menjadi lebih cepat.

**Kelima, bobot berpengaruh.** Rata-rata kesamaan anggota Top 10 dengan bobot sama pada tiga komponen adalah 0,8668 (Jaccard), minimum 0,4286. Varian persistensi lebih besar rata-rata 0,7931 dan minimum 0,25. Jadi urutan belum boleh dinyatakan optimal. Perbedaan ini bukan perbandingan langsung terhadap empat komponen Kaka.

**Keenam, sekolah tetap konteks.** Ada 17.278 entri sekolah yang lolos penyaringan referensi. Median jarak dari titik representatif area-hari sekitar 2,843 km. Angka ini memakai unit yang berbeda dari median jarak seluruh deteksi; jangan mencampurnya dengan 2,71/2,79 km versi lama. Kedekatan tidak membuktikan sekolah atau siswa terdampak.

## Apa yang dipakai dari versi sebelumnya?

| Sumber | Dipakai | Tidak diadopsi sebagai fakta/aturan |
|---|---|---|
| Maria / main | Struktur eksplorasi, gagasan dashboard dan dokumentasi; kode asli diarsipkan | Cuaca digeser tahunnya, kedekatan sekolah otomatis kritis, klaim gambut/water bombing, dan angka lama tanpa scope yang sama |
| Kaka / HTML v2 | Inspirasi peta, heatmap, rincian area; geometri 56 kab/kota | Bobot empat komponen 25% langsung menjadi baseline resmi; ranking dan skor lama |
| Evan / baseline v2 | Pengelompokan area-hari, audit, penjelasan batas data, bobot awal 40/35/25 | Persistensi berbasis jumlah deteksi tujuh hari; kini diganti hari aktif yang berbeda |

Riwayat repo yang diperiksa: main `5a962314d4d370b3daf505cdfaf6f1b50ed23903`, eda-kaka `dd89b49eb0da43ed2a4a0ada6adfb7a7d5008a93`, checkpoint2-evan `8c0d34231e68a5ea809d819e587455fd86ec6877`. Ini snapshot audit, bukan jaminan tidak ada push berikutnya. Tidak dilakukan merge lintas branch yang riwayatnya berbeda.

## Yang perlu direview sebelum menjadi acuan tim

1. **Granularitas tampilan:** grid 0,1° kira-kira 11 km; apakah cocok untuk Mapping community? Ini unit analitik, bukan radius dampak. Nama kab/kota bisa berulang di Top 10.
2. **Bobot dan batas P1/P2/P3:** aturan eksploratif yang sudah diuji sensitivitas, tetapi belum dikalibrasi dengan kejadian lapangan maupun kebutuhan pengguna.
3. **Sumber geometri kab/kota:** asal dan tahun versi Kaka belum tercantum. Sebanyak 56 area-hari belum memperoleh label kab/kota. BIG tetap acuan penyaringan scope.
4. **Makna jarak:** saat ini jarak ke sekolah, bukan jarak dari warga. Bila keputusan UX meminta jarak pengguna, perlu penyamaan definisi; tidak boleh diganti diam-diam.
5. **Batas waktu:** data berakhir Mei 2026. Dataset historis ini tidak dapat dipakai untuk mengaku kondisi terkini atau memvalidasi laporan baru. Urutan akhir hari juga bukan simulasi real-time; belum ada timestamp penerimaan data.

## Kesesuaian dengan UX Figma

Alur utamanya sudah sama: pengguna memilih tanggal/wilayah, melihat peta dan urutan prioritas, lalu membuka detail titik. HTML paling dekat dengan rancangan detail karena menampilkan status risiko, alasan kontribusi skor, koordinat, waktu terakhir, kualitas deteksi, konteks sekolah, dan sumber. Tableau berfungsi sebagai dashboard analitik; tooltip-nya memuat nilai inti yang sama tetapi tidak menampilkan jarak dari lokasi pengguna atau nama kecamatan.

Jarak yang tersedia adalah jarak garis lurus ke sekolah terdekat, bukan jarak ke perangkat pengguna. Nama kecamatan, geolokasi warga, laporan warga, notifikasi, dan luas terdampak belum ada di dataset utama sehingga tidak boleh ditampilkan seolah-olah sudah tersedia.

## Jawaban untuk pertanyaan Ryan / alignment case study

- **Sumber data:** checkpoint ini memakai snapshot dataset FIRMS yang disediakan proyek sebagai sumber utama. BIG dipakai untuk batas wilayah dan dataset sekolah Kaggle hanya sebagai konteks. NASA FIRMS dan BMKG belum diintegrasikan sebagai API/live feed; karena itu dashboard tidak mengklaim kondisi terkini.
- **Risk scoring:** DSA menetapkan definisi unit, komponen, bobot 40%/35%/25%, dan aturan P1/P2/P3 untuk prototipe; implementasi sistem hanya menjalankan aturan deterministik tersebut. Ini bukan model prediktif dan bukan keputusan operasional otomatis.
- **Peta:** HTML memakai Leaflet dengan basemap CARTO; Tableau memakai peta native Tableau. Provider peta hanya untuk visualisasi dan tidak mengubah data, skor, atau ranking.
- **Klik titik:** HTML menampilkan panel detail lengkap. Tableau menampilkan tooltip dengan nilai inti yang sama (area, prioritas, skor, observasi, persistensi, FRP, koordinat, sekolah, waktu, sumber, dan caveat luas terdampak), tetapi tidak meniru panel kontribusi HTML satu per satu.
- **Laporan warga/relawan:** belum menjadi input pada checkpoint ini. Jika fitur tersebut ditambahkan, laporan warga menjadi sinyal yang didispatch ke relawan untuk verifikasi; bukan langsung dianggap bukti kebakaran.

## Batas klaim yang sengaja dipertahankan

Tidak menyimpulkan verifikasi 12–24 jam dari jam lintasan satelit. Tidak menyimpulkan sebab-akibat cuaca, prediksi, luas terbakar dari ukuran piksel, kejadian gambut dari malam/FRP saja, kebutuhan water bombing, dampak sekolah, atau validitas laporan warga. Angka dari tiga versi tidak digabung sebelum satuan, periode, batas wilayah, dan aturan filternya disamakan.

## Berkas lokal dan rencana berbagi

CSV mentah/hasil, konfigurasi jalur lokal, cache, payload HTML, dan naskah pribadi tidak dipush. Notebook, modul yang dibutuhkan, template dashboard, tes, serta dokumentasi dapat dipertimbangkan setelah review. HTML keluaran menyematkan data lokasi sehingga dikecualikan dari Git secara default. Tidak ada file mirror `.py` dari kedua notebook.

Lihat `QA_REPORT.md` untuk hasil pengujian. Commit final `ebd4129` tersedia di branch remote `checkpoint3`; berkas kerja lama di luar paket ini tidak diubah.
