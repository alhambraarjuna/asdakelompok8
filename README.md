# AgroTrace Carbon Passport — Kopi Arabika Gayo Natural (200 g)

Aplikasi web ketertelusuran rantai pasok 7 tahap dan kalkulator jejak karbon untuk produk **Kopi Arabika Gayo Natural (Medium Roast, 200 g)**.

## Struktur Folder
```text
├── app.py                      # Aplikasi web utama (Streamlit)
├── agrotrace_lib.py            # Modul perhitungan karbon & audit rantai pasok
├── uji_app.py                  # Skrip pengujian otomatis (unit test)
├── requirements.txt            # Daftar pustaka Python untuk deployment
├── data/
│   ├── faktor_emisi.csv        # Daftar faktor konversi emisi & sumber rujukan
│   ├── paspor.json             # Dokumen paspor gabungan per batch
│   ├── emisi_per_batch.csv     # Ringkasan hasil perhitungan emisi per batch
│   ├── kebun.csv               # Data tahap 1: Kebun
│   ├── lot_panen.csv           # Data tahap 2: Lot Panen
│   ├── pascapanen.csv          # Data tahap 3: Pascapanen Natural
│   ├── green_bean.csv          # Data tahap 4: Green Bean
│   ├── roasting.csv            # Data tahap 5: Batch Roasting
│   ├── barang_jadi.csv         # Data tahap 6: Kemasan Barang Jadi 200 g
│   └── distribusi.csv          # Data tahap 7: Rute Distribusi
└── scripts/
    ├── 1_buat_data.py          # Pembuat data simulasi
    ├── 2_buat_paspor.py        # Penggabung rantai 7 tahap & hitung karbon
    └── 4_unggah_mongodb.py     # Pengunggah dokumen paspor ke MongoDB Atlas
```

## Cara Menjalankan di Lokal
```bash
pip install -r requirements.txt
python uji_app.py
streamlit run app.py
```

## Cara Deploy ke Streamlit Community Cloud
1. Unggah seluruh isi folder ini ke repositori GitHub Anda.
2. Buka [share.streamlit.io](https://share.streamlit.io) dan klik **Create app**.
3. Pilih repositori GitHub Anda, branch `main`, dan isi **Main file path** dengan `app.py`.
4. Klik **Deploy!**
