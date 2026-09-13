# Impor FIRELINE ke Power BI

Di halaman Power BI yang menampilkan **Add data to start building a report**, pilih **CSV**.

Pilih file lokal:

`review_outputs/FIRELINE_PowerBI_AreaDay.csv`

File ini adalah tabel presentasi area-hari, bukan CSV mentah. Satu baris berarti satu area grid pada satu tanggal UTC. Kolomnya sudah mencakup koordinat, provinsi, kabupaten/kota, jumlah observasi, aktivitas tujuh hari, FRP, confidence, skor, tingkat prioritas, dan jarak ke sekolah.

## Visual yang disarankan

1. **Map:** Latitude = `latitude`, Longitude = `longitude`, Size = `satellite_observations`, Legend = `priority_level`, Tooltips = `area_grid_id`, `province`, `kabupaten_kota`, `priority_score`, `quality_note`.
2. **Line chart tren:** X-axis = `observation_date_utc`, Y-axis = sum `satellite_observations`, Legend = `province`.
3. **Bar chart exposure:** Axis = `province` atau bucket `nearest_school_distance_km`, Values = count `area_grid_id` atau sum `satellite_observations`. Jelaskan bahwa ini konteks kedekatan sekolah, bukan bukti sekolah terdampak.
4. **Top 10 table:** Filter tanggal, sort `priority_score` descending, tampilkan `area_grid_id`, `province`, `kabupaten_kota`, `priority_score`, `priority_level`, `satellite_observations`, `active_days_last_7`.
5. **Slicer:** `observation_date_utc`, `province`, dan `priority_level`.

## Catatan penting

- Gunakan `observation_date_utc` sebagai tanggal; data historis berakhir 31 Mei 2026.
- Peta ini menunjukkan urutan perhatian provisional, bukan prediksi, tingkat keparahan, confidence satelit, atau status kebakaran terverifikasi.
- P1/P2/P3 adalah aturan sementara: P1 ≥80, P2 60–<80, P3 <60.
- `nearest_school_distance_km` adalah jarak garis lurus dari observasi representatif ke sekolah terdekat pada dataset referensi. Jangan menyebutnya sebagai radius dampak atau jumlah warga terdampak.
- Jika Power BI menampilkan pilihan penyimpanan, simpan hanya di workspace yang memang disetujui tim. Tidak ada koneksi MCP otomatis pada sesi ini; impor dilakukan melalui UI Power BI.

Untuk membangun ulang file setelah pipeline berubah:

```powershell
python -m fireline.export_powerbi
```
