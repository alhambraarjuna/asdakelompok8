"""
scripts/2_buat_paspor.py — Penggabung Rantai 7 Tahap, Kalkulasi Karbon & Audit Kelengkapan
"""
import json
from agrotrace_lib import gabungkan_rantai_dari_csv

def main():
    daftar_paspor = gabungkan_rantai_dari_csv("data")
    with open("data/paspor.json", "w", encoding="utf-8") as f:
        json.dump(daftar_paspor, f, indent=2, ensure_ascii=False)
    print(f"Berhasil membuat data/paspor.json untuk {len(daftar_paspor)} batch.")

if __name__ == "__main__":
    main()
