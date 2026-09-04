# Roadmap DSA menuju Checkpoint 2

## Posisi saat ini

Tahap yang sudah memiliki implementasi/output awal (bukan seluruhnya tervalidasi):

- EDA lengkap FIRMS;
- audit dataset eksternal;
- feature engineering grid-hari;
- spatial join provinsi dan sekolah;
- temporal-spatial join cuaca berdasarkan label tanggal, dengan koreksi UTC–LST masih tertunda;
- skor prioritas provisional;
- ablation test;
- low-fidelity dashboard;
- data contract lintas role.

## Gate sebelum model prediksi

Selesaikan dahulu penyelarasan UTC–LST dan audit cakupan daratan cuaca.
Korelasi yang tersimpan belum dihitung ulang dan tidak menjadi fakta PRD.

Jangan langsung menamai model sebagai prediksi kebakaran. Tim harus memilih salah
satu target berikut:

1. **Prioritization-only:** mempertahankan heuristik dan memvalidasi urutan P1
   bersama mentor/domain expert.
2. **Predictive research extension:** memprediksi apakah satelit akan kembali
   mengamati anomali panas pada grid dalam satu hari ke depan.

Target kedua tetap memprediksi observasi FIRMS, bukan kebakaran terverifikasi.

## Jika mentoring memilih prioritization-only

- minta mentor menilai tiga komponen dan bobot;
- uji beberapa bobot lalu bandingkan kestabilan P1;
- tentukan jumlah area yang realistis diperiksa per hari;
- ubah percentile menjadi kapasitas antrean yang disepakati;
- ukur apakah operator dapat menjelaskan alasan P1.

## Jika mentoring mewajibkan model training

Baseline yang aman:

- naive persistence: grid aktif besok jika aktif hari ini;
- logistic regression sebagai model yang mudah dijelaskan;
- tree-based model sebagai pembanding nonlinear.

Aturan evaluasi:

- fitur hanya boleh memakai informasi sebelum tanggal target;
- split train, validation, dan test harus berdasarkan waktu;
- tanggal tanpa observasi harus dimasukkan sebagai contoh negatif;
- gunakan precision, recall, F1, PR-AUC, dan false-negative rate;
- bandingkan dengan naive persistence;
- jangan memakai accuracy saja karena target kemungkinan tidak seimbang;
- laporkan hasil sebagai prediksi observasi satelit, bukan prediksi kebakaran.

## Output yang disiapkan untuk SEA

SEA cukup memakai data_contract.json untuk menggambar:

- ingestion FIRMS dan data eksternal;
- feature processing;
- penyimpanan grid-hari;
- conceptual API;
- dashboard consumer.

Deployment dan REST API nyata hanya dibuat jika aturan checkpoint menyatakannya
sebagai implementasi wajib.
