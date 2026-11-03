"""
agrotrace_lib.py — Modul Inti Kalkulasi Jejak Karbon & Ketertelusuran Rantai Pasok
Produk: Kopi Arabika Gayo Natural (Medium Roast, Kemasan 200 g)
"""

import os
import json
import math
import pandas as pd


TAHAPAN_RANTAI = [
    "kebun",
    "lot_panen",
    "pascapanen",
    "green_bean",
    "roasting",
    "barang_jadi",
    "distribusi",
]

FIELD_WAJIB_PER_TAHAP = {
    "kebun": ["id_kebun", "kecamatan", "pupuk_n_kg"],
    "lot_panen": ["id_lot_panen", "tanggal_panen", "bobot_cherry_kg", "solar_angkut_liter"],
    "pascapanen": ["id_pascapanen", "metode", "durasi_jemur_hari", "solar_huller_liter"],
    "green_bean": ["id_green_bean", "bobot_green_bean_kg", "skor_cupping", "jumlah_karung"],
    "roasting": ["id_roasting", "profil_roast", "lpg_kg", "listrik_kwh"],
    "barang_jadi": ["id_batch", "jumlah_pouch_200g", "bobot_kemasan_total_kg"],
    "distribusi": ["id_distribusi", "rute", "jarak_km"],
}


def _is_valid_value(val):
    if val is None:
        return False
    if isinstance(val, float) and math.isnan(val):
        return False
    if isinstance(val, str) and val.strip() == "":
        return False
    return True


def _safe_float(val, default=0.0):
    if not _is_valid_value(val):
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def muat_faktor_emisi(path_csv="data/faktor_emisi.csv"):
    """Memuat tabel faktor emisi ke dalam DataFrame dan kamus pencari cepat."""
    df = pd.read_csv(path_csv)
    fe_map = {}
    for _, row in df.iterrows():
        fe_map[row["id_faktor"]] = {
            "tahap": row["tahap"],
            "komponen": row["komponen"],
            "satuan": row["satuan"],
            "nilai_fe": float(row["nilai_fe"]),
            "satuan_emisi": row["satuan_emisi"],
            "sumber": row["sumber"],
            "status": row["status"],
        }
    return df, fe_map


def audit_kelengkapan_batch(dokumen_batch):
    """
    Memeriksa kelengkapan data aktivitas di seluruh 7 tahap rantai pasok.
    Mengembalikan skor kelengkapan (%), status audit, dan daftar field kosong.
    """
    rantai = dokumen_batch.get("rantai_pasok", {})
    total_field = 0
    field_terisi = 0
    field_kosong = []

    for tahap in TAHAPAN_RANTAI:
        data_tahap = rantai.get(tahap, {})
        wajib = FIELD_WAJIB_PER_TAHAP.get(tahap, [])
        for f in wajib:
            total_field += 1
            if _is_valid_value(data_tahap.get(f)):
                field_terisi += 1
            else:
                field_kosong.append(f"{tahap}.{f}")

    skor = round((field_terisi / total_field) * 100.0, 1) if total_field > 0 else 0.0
    status = "Terverifikasi Lengkap" if len(field_kosong) == 0 else "Data Parsial"
    return {
        "skor_kelengkapan_persen": skor,
        "status_audit": status,
        "field_kosong": field_kosong,
        "jumlah_field_kosong": len(field_kosong),
    }


def hitung_emisi_batch(dokumen_batch, fe_map):
    """
    Menghitung ulang emisi karbon (Emisi = Aktivitas x Faktor Emisi) secara dinamis
    untuk setiap tahapan proses dan per kemasan 200 g.
    """
    rantai = dokumen_batch.get("rantai_pasok", {})

    kebun = rantai.get("kebun", {})
    panen = rantai.get("lot_panen", {})
    pascapanen = rantai.get("pascapanen", {})
    green_bean = rantai.get("green_bean", {})
    roasting = rantai.get("roasting", {})
    barang_jadi = rantai.get("barang_jadi", {})
    distribusi = rantai.get("distribusi", {})

    emisi_kebun = _safe_float(kebun.get("pupuk_n_kg")) * fe_map["FE-01"]["nilai_fe"]
    emisi_panen = _safe_float(panen.get("solar_angkut_liter")) * fe_map["FE-02"]["nilai_fe"]
    emisi_pascapanen = _safe_float(pascapanen.get("solar_huller_liter")) * fe_map["FE-03"]["nilai_fe"]
    emisi_green_bean = _safe_float(green_bean.get("jumlah_karung")) * fe_map["FE-04"]["nilai_fe"]

    emisi_roasting_lpg = _safe_float(roasting.get("lpg_kg")) * fe_map["FE-05"]["nilai_fe"]
    emisi_roasting_listrik = _safe_float(roasting.get("listrik_kwh")) * fe_map["FE-06"]["nilai_fe"]
    emisi_roasting = emisi_roasting_lpg + emisi_roasting_listrik

    emisi_kemasan = _safe_float(barang_jadi.get("bobot_kemasan_total_kg")) * fe_map["FE-07"]["nilai_fe"]
    emisi_distribusi = _safe_float(distribusi.get("jarak_km")) * fe_map["FE-08"]["nilai_fe"]

    rincian_tahap = {
        "kebun": round(emisi_kebun, 3),
        "lot_panen": round(emisi_panen, 3),
        "pascapanen": round(emisi_pascapanen, 3),
        "green_bean": round(emisi_green_bean, 3),
        "roasting": round(emisi_roasting, 3),
        "barang_jadi": round(emisi_kemasan, 3),
        "distribusi": round(emisi_distribusi, 3),
    }

    rincian_komponen = {
        "Pupuk N (Kebun)": round(emisi_kebun, 3),
        "Solar Panen & Huller": round(emisi_panen + emisi_pascapanen, 3),
        "Karung Green Bean": round(emisi_green_bean, 3),
        "LPG Roasting": round(emisi_roasting_lpg, 3),
        "Listrik Roasting": round(emisi_roasting_listrik, 3),
        "Kemasan Pouch 200 g": round(emisi_kemasan, 3),
        "Logistik Distribusi": round(emisi_distribusi, 3),
    }

    total_emisi_batch = round(sum(rincian_tahap.values()), 3)
    jumlah_pouch = max(int(_safe_float(barang_jadi.get("jumlah_pouch_200g"), 1)), 1)
    emisi_per_pouch = round(total_emisi_batch / jumlah_pouch, 4)

    audit = audit_kelengkapan_batch(dokumen_batch)

    return {
        "id_batch": dokumen_batch.get("id_batch"),
        "jumlah_pouch_200g": jumlah_pouch,
        "total_emisi_batch_kg": total_emisi_batch,
        "emisi_per_200g_kg": emisi_per_pouch,
        "rincian_tahap": rincian_tahap,
        "rincian_komponen": rincian_komponen,
        "audit": audit,
    }


def gabungkan_rantai_dari_csv(folder_data="data"):
    """Menggabungkan 7 tabel CSV menjadi list dokumen paspor batch yang utuh."""
    kebun_df = pd.read_csv(os.path.join(folder_data, "kebun.csv")).where(pd.notnull, None)
    panen_df = pd.read_csv(os.path.join(folder_data, "lot_panen.csv")).where(pd.notnull, None)
    pascapanen_df = pd.read_csv(os.path.join(folder_data, "pascapanen.csv")).where(pd.notnull, None)
    gb_df = pd.read_csv(os.path.join(folder_data, "green_bean.csv")).where(pd.notnull, None)
    roast_df = pd.read_csv(os.path.join(folder_data, "roasting.csv")).where(pd.notnull, None)
    bj_df = pd.read_csv(os.path.join(folder_data, "barang_jadi.csv")).where(pd.notnull, None)
    dist_df = pd.read_csv(os.path.join(folder_data, "distribusi.csv")).where(pd.notnull, None)

    _, fe_map = muat_faktor_emisi(os.path.join(folder_data, "faktor_emisi.csv"))

    kebun_map = {r["id_kebun"]: r.to_dict() for _, r in kebun_df.iterrows()}
    panen_map = {r["id_lot_panen"]: r.to_dict() for _, r in panen_df.iterrows()}
    pascapanen_map = {r["id_pascapanen"]: r.to_dict() for _, r in pascapanen_df.iterrows()}
    gb_map = {r["id_green_bean"]: r.to_dict() for _, r in gb_df.iterrows()}
    roast_map = {r["id_roasting"]: r.to_dict() for _, r in roast_df.iterrows()}
    dist_map = {r["id_batch"]: r.to_dict() for _, r in dist_df.iterrows()}

    daftar_paspor = []
    for _, bj_row in bj_df.iterrows():
        bj = bj_row.to_dict()
        id_batch = bj["id_batch"]
        roast = roast_map.get(bj.get("id_roasting"), {})
        gb = gb_map.get(roast.get("id_green_bean"), {})
        pascapanen = pascapanen_map.get(gb.get("id_pascapanen"), {})
        panen = panen_map.get(pascapanen.get("id_lot_panen"), {})
        kebun = kebun_map.get(panen.get("id_kebun"), {})
        dist = dist_map.get(id_batch, {})

        # Bersihkan NaN agar kompatibel dengan JSON
        def clean_dict(d):
            return {k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in d.items()}

        dokumen = {
            "id_batch": id_batch,
            "produk": bj.get("nama_produk", "Kopi Arabika Gayo Natural 200 g"),
            "rantai_pasok": {
                "kebun": clean_dict(kebun),
                "lot_panen": clean_dict(panen),
                "pascapanen": clean_dict(pascapanen),
                "green_bean": clean_dict(gb),
                "roasting": clean_dict(roast),
                "barang_jadi": clean_dict(bj),
                "distribusi": clean_dict(dist),
            },
        }
        hasil_hitung = hitung_emisi_batch(dokumen, fe_map)
        dokumen["ringkasan_karbon"] = hasil_hitung
        daftar_paspor.append(dokumen)

    return daftar_paspor
