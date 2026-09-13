# Integrasi hasil Kaka — checkpoint 3

Bagian yang digabungkan dari branch `kaka-checkpoint3`:

- hierarki kabupaten/kota pada payload dan batas tampilan (56 fitur);
- filter provinsi → kabupaten/kota, mode satu tanggal vs seluruh riwayat, serta tombol tanggal sebelumnya/berikutnya;
- klik poligon untuk memilih kabupaten/kota;
- helper `fetch_fireline_dataset.py` untuk mengambil bundle yang sama dari Hugging Face secara eksplisit.

Skor utama, bobot, ranking Top 10, dan angka audit tetap memakai pipeline checkpoint 3. Mode riwayat hanya untuk membaca pola historis dan tidak boleh dipakai sebagai kondisi real-time. Populasi dan geometri tambahan bersifat konteks; keduanya tidak mengubah skor.

## Perbaikan saat integrasi

Payload Kaka memakai nama properti `kabupaten_code`/`kabupaten_name`, sedangkan template awal mengharapkan `region_id`/`region_name`. Template sekarang menerima kedua bentuk sehingga warna poligon, tooltip, dan klik filter tetap bekerja. Peta dasar tetap memakai CARTO agar review lokal tidak terkena blokir tile server OSM publik.

Tidak ada perubahan ke GitHub pada pekerjaan ini.
