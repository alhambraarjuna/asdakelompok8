"""
uji_app.py — Pengujian Otomatis Logika Karbon, Kelengkapan Rantai, & Penanganan Data Kosong
"""
import unittest
from agrotrace_lib import muat_faktor_emisi, gabungkan_rantai_dari_csv, hitung_emisi_batch

class TestAgroTrace(unittest.TestCase):
    def setUp(self):
        self.df_fe, self.fe_map = muat_faktor_emisi("data/faktor_emisi.csv")
        self.paspor_list = gabungkan_rantai_dari_csv("data")

    def test_01_jalur_normal_perhitungan_ulang(self):
        """Pastikan batch lengkap dihitung emisinya dengan benar."""
        batch_1 = next(b for b in self.paspor_list if b["id_batch"] == "GAYO-NAT-2601")
        hasil = hitung_emisi_batch(batch_1, self.fe_map)
        self.assertGreater(hasil["total_emisi_batch_kg"], 0)
        self.assertGreater(hasil["emisi_per_200g_kg"], 0)
        self.assertEqual(hasil["audit"]["status_audit"], "Terverifikasi Lengkap")
        self.assertEqual(hasil["audit"]["skor_kelengkapan_persen"], 100.0)

    def test_02_data_aktivitas_parsial_kosong(self):
        """Pastikan field kosong terdeteksi sebagai Data Parsial tanpa menyebabkan crash."""
        batch_5 = next(b for b in self.paspor_list if b["id_batch"] == "GAYO-NAT-2605")
        hasil = hitung_emisi_batch(batch_5, self.fe_map)
        self.assertEqual(hasil["audit"]["status_audit"], "Data Parsial")
        self.assertGreater(hasil["audit"]["jumlah_field_kosong"], 0)
        self.assertGreater(hasil["total_emisi_batch_kg"], 0)

    def test_03_transparansi_status_faktor_emisi(self):
        """Pastikan setiap faktor emisi memiliki status Bersumber atau Asumsi."""
        status_valid = {"Bersumber", "Asumsi"}
        for _, row in self.df_fe.iterrows():
            self.assertIn(row["status"], status_valid)

if __name__ == "__main__":
    unittest.main(verbosity=2)
