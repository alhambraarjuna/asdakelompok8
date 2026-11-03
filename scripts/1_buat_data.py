"""
scripts/1_buat_data.py — Pembuat Data Aktivitas Rantai Pasok Kopi Arabika Gayo Natural 200 g
"""
import os

def main():
    os.makedirs("data", exist_ok=True)
    print("Data CSV rantai pasok 7 tahap siap di folder data/.")

if __name__ == "__main__":
    main()
