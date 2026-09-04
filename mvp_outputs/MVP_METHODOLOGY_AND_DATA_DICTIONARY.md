# FIRELINE MVP — Metodologi dan Data Dictionary

**Status review:** cuaca masih dicocokkan berdasarkan label tanggal, sementara
FIRMS memakai UTC dan cache POWER memakai LST. Cakupan 100% bukan bukti kesamaan
jendela waktu. Output cuaca/korelasi/panel dashboard belum dihitung ulang dan
tidak boleh menjadi fakta PRD. Cuaca tidak masuk skor. Lihat ../REVIEW_STATUS.md.

## Ringkasan hasil pipeline

| Metrik | Hasil |
|---|---:|
| Observasi FIRMS | 61.583 |
| Grid unik 0,1 derajat | 2.954 |
| Unit grid-hari | 27.411 |
| Periode | 1 Agustus 2024–31 Mei 2026 |
| Cakupan label lima provinsi | 97,10% |
| Unit tanpa label provinsi | 796 grid-hari / 177 grid unik |
| Cakupan cuaca NASA POWER | 100% |
| Median jarak pusat grid ke sekolah terdekat atas seluruh baris grid-hari | 2,94 km |
| Total baris P1 provisional | 3.114 |
| P1 pada tanggal demo 3 September 2024 | 51 |

## Unit analisis

Kunci utama adalah kombinasi **grid_id + date**.

- grid_id dibentuk dari pembulatan ke bawah koordinat pada resolusi 0,1 derajat.
- Pusat grid dipakai untuk spatial join ke provinsi, sekolah, dan node cuaca.
- Beberapa observasi pada grid dan hari yang sama menjadi satu kandidat area.

Agregasi mengurangi 61.583 observasi mentah menjadi 27.411 grid-hari. Artinya
jumlah baris antrean berkurang sekitar 55,5%, tetapi angka ini belum membuktikan
penghematan waktu petugas.

## Rumus prioritas

Setiap komponen diranking relatif terhadap grid aktif lain pada tanggal yang sama.

**priority score = 100 × (0,40 activity + 0,35 persistence + 0,25 intensity)**

- activity: percentile jumlah observasi pada hari tersebut;
- persistence: percentile total observasi pada tujuh hari terakhir di grid sama;
- intensity: percentile median FRP.

Label:

- P1: percentile skor harian minimal 90%;
- P2: percentile skor harian 70% sampai kurang dari 90%;
- P3: percentile skor harian di bawah 70%.

Angka dan bobot tersebut merupakan **heuristik MVP**. Skor bukan probabilitas dan
belum boleh disebut sebagai tingkat risiko resmi.

## Hasil uji sensitivitas

| Komponen yang dihapus | Jaccard anggota P1 | Baris yang berubah |
|---|---:|---:|
| Aktivitas hari ini | 0,555 | 1.784 |
| Intensitas FRP | 0,567 | 1.693 |
| Persistensi tujuh hari | 0,639 | 1.374 |

Daftar P1 masih berubah cukup banyak ketika satu komponen dihilangkan. Kesimpulan:
bobot perlu dibahas dengan mentor/domain expert dan tidak boleh dianggap final.

## Data dictionary

| Kolom | Arti untuk pembaca nonteknis | Peran |
|---|---|---|
| grid_id | Identitas area kecil pada peta | Kunci |
| date | Tanggal observasi | Kunci |
| grid_center_lat | Posisi utara–selatan pusat area | Peta |
| grid_center_lon | Posisi barat–timur pusat area | Peta |
| province_code | Kode provinsi BIG | Filter |
| province_name | Nama provinsi | Filter |
| detection_count | Banyaknya observasi satelit pada area dan hari itu | Skor |
| detections_7d | Total observasi tujuh hari terakhir pada area sama | Skor |
| active_days_7d | Berapa hari area muncul dalam tujuh hari terakhir | Penjelas |
| frp_median_mw | Nilai tengah kekuatan radiasi panas | Skor |
| frp_max_mw | Nilai FRP tertinggi pada area dan hari itu | Detail |
| high_conf_share | Bagian observasi dengan confidence tinggi | Kualitas |
| low_conf_share | Bagian observasi dengan confidence rendah | Kualitas |
| night_share | Bagian observasi yang diperoleh malam hari | Konteks |
| priority_score | Skor urutan provisional 0–100 | Output |
| priority_percentile_daily | Posisi relatif dibanding area aktif lain hari itu | Output |
| priority_level | P1, P2, atau P3 | Output |
| primary_reason | Komponen terbesar yang mendorong skor | Explainability |
| quality_status | Peringatan data terbatas atau perlu diperiksa | Guardrail |
| nearest_school_distance_km | Jarak pusat area ke sekolah terdekat | Konteks |
| nearest_school_name | Nama sekolah terdekat | Konteks |
| weather_distance_km | Jarak pusat area ke node cuaca terdekat | Kualitas join |
| PRECTOTCORR | Estimasi hujan harian | Konteks |
| PRECTOTCORR_7d | Akumulasi hujan tujuh hari | Konteks |
| T2M | Suhu udara dua meter | Konteks |
| RH2M | Kelembapan relatif dua meter | Konteks |
| WS2M | Kecepatan angin dua meter | Konteks |

## Perbedaan angka jarak sekolah

Analisis mentah sebelumnya memperoleh median sekitar 2,79 km pada tingkat
observasi FIRMS. Pipeline MVP memperoleh 2,94 km dari seluruh baris grid-hari:
jarak pusat grid yang sama diulang pada setiap tanggal aktifnya. Angka ini bukan
median atas grid unik yang masing-masing dihitung sekali. Kedua angka memakai
unit analisis berbeda. Untuk narasi EDA
mentah gunakan 2,79 km; untuk penjelasan tabel MVP gunakan 2,94 km.

## Guardrail

- FIRMS mendeteksi anomali panas, bukan kebakaran yang telah diverifikasi.
- FRP menggambarkan kekuatan radiasi relatif, bukan luas kebakaran.
- Confidence menggambarkan kualitas deteksi, bukan tingkat bahaya.
- Kedekatan sekolah tidak membuktikan sekolah atau warga terdampak.
- Korelasi cuaca tidak membuktikan penyebab.
- Label P1 tidak menggantikan verifikasi dan keputusan manusia.
