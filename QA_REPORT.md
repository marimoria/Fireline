# Hasil Pengujian Lokal

10 September 2026 — `priority-map-1.0`. Pengujian teknis tidak sama dengan validasi manfaat atau keamanan operasional.

## Otomatis

**10 tes lulus** (`python -m pytest -q`, 9,35 detik pada lingkungan lokal setelah pembersihan peringatan tes).

- Jendela persistensi mengikuti hari kalender dan tidak memakai tanggal masa depan.
- Semua 26.773 area-hari diperiksa ulang terhadap hitungan kalender independen.
- Jumlah observasi sebelum/sesudah audit dan pengelompokan konsisten.
- Kunci area-tanggal unik; confidence per area menjumlah ke total observasi.
- Rentang skor dan jumlah kontribusi komponen konsisten.
- Kasus satu area dan nilai seri tidak mendapat persentil maksimum buatan.
- Titik tepat di batas dua provinsi tidak dihitung ganda.
- HHMM tidak valid ditolak; FRP negatif/tidak hingga dicatat kosong.
- Data HTML mengikuti urutan skor/tie-break notebook dan teks masukan di-escape.
- Kedua notebook memiliki hasil eksekusi tanpa error; pembungkus Streamlit lolos AppTest tanpa exception.

Kedua notebook dijalankan dari awal dengan `nbconvert --execute`. Pipeline berhasil membangun ulang HTML dari sumber lokal. Pembaca GeoJSON memberi peringatan tentang dimensi tambahan koordinat BIG; analisis menggunakan lintang/bujur dua dimensi. Peringatan tidak mengubah jumlah koordinat horizontal, tetapi tetap dicatat sebagai karakteristik berkas sumber.

## Interaksi browser

| Skenario | Hasil teramati |
|---|---|
| Demo 3 September 2024 | 2.399 observasi, 505 area, 1 P1; detail awal Sintang |
| Filter Kalimantan Utara pada tanggal demo | 0 area, pesan kosong; tidak menampilkan data provinsi sebelumnya |
| Kalimantan Utara, 2 September 2024 | 27 observasi, 16 area, 0 P1; detail WITA |
| Filter P1 pada kombinasi tanpa P1 | Daftar dan detail kosong dengan penjelasan, bukan label aman |
| Klik baris Top 10 | Detail, kontribusi dan grid berubah sesuai baris terpilih |
| Klik marker yang tidak tertutup marker lain | Detail berubah ke area marker terkait |
| Lapisan peta | Heatmap, area observasi, nomor Top 10 dan poligon dapat diaktifkan |
| Tanggal dikosongkan | Grafik lama dibersihkan; muncul permintaan memilih tanggal |
| Reset demo | Kembali ke tanggal/provinsi awal dengan 2.399 observasi |
| Desktop 1280×900 dan mobile 390×844 | Layout menyesuaikan; mobile tidak memiliki overflow horizontal (lebar konten = lebar halaman 375 px) |
| Console browser | Tidak ada error pada sesi pengujian |

Catatan UX: nomor di wilayah padat dapat bertumpuk pada zoom seluruh Kalimantan; klik dapat mengenai marker paling depan. Daftar Top 10 dan zoom tersedia sebagai pilihan yang tidak ambigu, dan petunjuk ditambahkan di atas peta. Jangan menafsirkan nomor bertumpuk sebagai ranking yang berbeda. Akses keyboard marker belum dinyatakan lolos; gunakan baris daftar yang berupa tombol untuk pemilihan area.

## Belum dinyatakan teruji

- Validasi bobot dengan kejadian lapangan, kapasitas pengguna, manfaat prioritas, dan usability bersama warga/relawan.
- Browser/device selain sesi desktop dan viewport mobile di atas; perangkat mobile fisik belum diuji.
- Gangguan jaringan nyata atau penggunaan sepenuhnya offline. Fallback pustaka peta disediakan, tetapi belum diuji dengan pemutusan koneksi. CDN Leaflet dan peta dasar membutuhkan internet.
- Integrasi live FIRMS, laporan warga, notifikasi, geolokasi pengguna, dispatch dan verifikasi lapangan: di luar lingkup implementasi ini.

## Pengamanan handoff

Tidak ada push/merge remote. File CSV, payload data, HTML keluaran, cache, dan konfigurasi lokal masuk daftar pengecualian Git. File lama dipindahkan ke arsip lokal dengan riwayat asal tetap tersedia. Sebelum publikasi, lakukan review sumber/lisensi geometri serta dataset sekolah dan review angka dalam notebook.
