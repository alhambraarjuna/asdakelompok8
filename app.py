"""
app.py — AgroTrace Carbon Passport & Traceability Web Application
Kopi Arabika Gayo Natural (Medium Roast, Kemasan 200 g)
"""

import io
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import qrcode

from agrotrace_lib import (
    muat_faktor_emisi,
    hitung_emisi_batch,
    gabungkan_rantai_dari_csv,
)

st.set_page_config(
    page_title="AgroTrace — Paspor Karbon Kopi Arabika Gayo Natural",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #FAFAFA;
        color: #141414;
    }
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 1.5rem;
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        margin-bottom: 2rem;
    }
    .pill-badge {
        display: inline-block;
        background: #F3F4F2;
        color: #1B4332;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 600;
        border: 1px solid #E5E7EB;
        margin-bottom: 0.75rem;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        line-height: 1.15;
        color: #141414;
        margin-bottom: 1rem;
    }
    .hero-sub {
        font-size: 1.05rem;
        color: #4B5563;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    .bento-card {
        background: #F4F5F4;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 1.5rem;
        height: 100%;
    }
    .white-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    }
    .status-ok {
        background: #DCFCE7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def muat_data_paspor():
    """Memuat dokumen paspor dari MongoDB Atlas (jika tersedia) atau fallback lokal."""
    df_fe, fe_map = muat_faktor_emisi("data/faktor_emisi.csv")
    dokumen_mentah = None

    try:
        if "mongo_uri" in st.secrets and st.secrets["mongo_uri"]:
            from pymongo import MongoClient
            client = MongoClient(st.secrets["mongo_uri"], serverSelectionTimeoutMS=3000)
            db = client["agrotrace_db"]
            docs = list(db["paspor_batch"].find({}, {"_id": 0}))
            if docs:
                dokumen_mentah = docs
    except Exception:
        dokumen_mentah = None

    if not dokumen_mentah:
        try:
            with open("data/paspor.json", "r", encoding="utf-8") as f:
                dokumen_mentah = json.load(f)
        except Exception:
            dokumen_mentah = gabungkan_rantai_dari_csv("data")

    for doc in dokumen_mentah:
        doc["ringkasan_karbon"] = hitung_emisi_batch(doc, fe_map)

    return dokumen_mentah, df_fe, fe_map


def buat_qr_bytes(teks_qr):
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(teks_qr)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#141414", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


daftar_paspor, df_fe, fe_map = muat_data_paspor()

# 1. TOP NAVIGATION BAR
st.markdown(
    """
    <div class="nav-bar">
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:1.4rem;">🌱</span>
            <span style="font-weight:800;font-size:1.25rem;letter-spacing:-0.02em;">AgroTrace</span>
        </div>
        <div style="color:#4B5563;font-size:0.9rem;font-weight:500;">
            Ketertelusuran Rantai Pasok · Kalkulator Jejak Karbon · QR Paspor Kemasan
        </div>
        <div>
            <span style="background:#141414;color:#FFFFFF;padding:8px 16px;border-radius:999px;font-size:0.82rem;font-weight:600;">
                Kopi Arabika Gayo Natural 200 g
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 2. HERO SECTION
col_hero_l, col_hero_r = st.columns([1.35, 1], gap="large")

with col_hero_l:
    st.markdown(
        '<div class="pill-badge">🌱 7 Tahap Rantai Pasok Terlacak · Kopi Arabika Gayo Natural 200 g</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-title">Kenali Asal-Usul & Jejak Karbon di Setiap Seduhan Kopi Gayo Anda</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-sub">Telusuri perjalanan biji kopi dari kebun dataran tinggi Gayo, proses penjemuran natural, penyangraian Medium Roast, hingga dikemas dalam pouch 200 gram secara transparan.</div>',
        unsafe_allow_html=True,
    )

with col_hero_r:
    sample = daftar_paspor[0]
    rk_sample = sample["ringkasan_karbon"]
    st.markdown(
        f"""
        <div class="white-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <span style="font-size:0.78rem;color:#6B7280;font-weight:600;">PRATINJAU PASPOR DIGITAL</span>
                <span class="status-ok">{rk_sample["audit"]["status_audit"]}</span>
            </div>
            <div style="font-size:1.25rem;font-weight:800;margin-bottom:4px;">Batch {sample["id_batch"]}</div>
            <div style="font-size:0.85rem;color:#4B5563;margin-bottom:14px;">
                Asal Kebun: {sample["rantai_pasok"]["kebun"].get("kecamatan")} ({sample["rantai_pasok"]["kebun"].get("ketinggian_mdpl")} mdpl)
            </div>
            <div style="background:#F4F5F4;padding:12px 16px;border-radius:12px;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:0.75rem;color:#6B7280;">Jejak Karbon per Kemasan 200 g</div>
                    <div style="font-size:1.6rem;font-weight:800;color:#1B4332;">{rk_sample["emisi_per_200g_kg"]:.3f} kg CO₂e</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.75rem;color:#6B7280;">Skor Cupping</div>
                    <div style="font-size:1.2rem;font-weight:700;">{sample["rantai_pasok"]["green_bean"].get("skor_cupping")} pts</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# 3. BENTO GRID FEATURES
st.markdown("### Keunggulan Transparansi AgroTrace")
b1_col1, b1_col2 = st.columns([3, 2])
with b1_col1:
    st.markdown(
        """
        <div class="bento-card">
            <h4 style="margin-top:0;">1. Penelusuran Utuh 7 Tahap Hulu ke Hilir</h4>
            <p style="color:#4B5563;margin-bottom:0;">
                Setiap kemasan 200 g mencatat riwayat lengkap mulai dari Kebun di dataran tinggi Gayo, Lot Panen Petik Merah, Pascapanen Jemur Natural, Green Bean, Batch Roasting Medium Roast, Kemasan Pouch, hingga Rute Distribusi.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with b1_col2:
    st.markdown(
        """
        <div class="bento-card">
            <h4 style="margin-top:0;">2. Perhitungan Jejak Karbon Langsung</h4>
            <p style="color:#4B5563;margin-bottom:0;">
                Angka emisi dihitung dari pemakaian energi dan material nyata di setiap tahap produksi, lalu dibagi secara proporsional per kemasan 200 gram.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
b2_col1, b2_col2 = st.columns([2, 3])
with b2_col1:
    st.markdown(
        """
        <div class="bento-card">
            <h4 style="margin-top:0;">3. Rujukan Faktor Emisi Terbuka</h4>
            <p style="color:#4B5563;margin-bottom:0;">
                Setiap komponen emisi mencantumkan nilai faktor konversi beserta sumber rujukannya secara jujur dan terbuka.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with b2_col2:
    st.markdown(
        """
        <div class="bento-card">
            <h4 style="margin-top:0;">4. Paspor QR Code Siap Unduh</h4>
            <p style="color:#4B5563;margin-bottom:0;">
                Hasilkan kode QR unik untuk setiap batch produksi yang dapat langsung diunduh dalam format gambar PNG dan ditempelkan pada kemasan kopi.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("---")

# 4. INTERACTIVE WORKSPACE
st.markdown("## Eksplorasi Batch & Paspor Karbon Kopi Gayo")

f_col1, f_col2, f_col3 = st.columns([1.2, 1.2, 1.6])
semua_kecamatan = sorted(list({p["rantai_pasok"]["kebun"].get("kecamatan", "-") for p in daftar_paspor}))
with f_col1:
    pilih_kecamatan = st.selectbox("Filter Asal Kebun (Kecamatan)", ["Semua Kecamatan"] + semua_kecamatan)
with f_col2:
    pilih_status = st.selectbox("Filter Status Data", ["Semua Status", "Terverifikasi Lengkap", "Data Parsial"])
with f_col3:
    cari_batch = st.text_input("Cari Kode Batch", placeholder="Contoh: GAYO-NAT-2601")

paspor_terfilter = []
for p in daftar_paspor:
    kec = p["rantai_pasok"]["kebun"].get("kecamatan", "-")
    st_audit = p["ringkasan_karbon"]["audit"]["status_audit"]
    if pilih_kecamatan != "Semua Kecamatan" and kec != pilih_kecamatan:
        continue
    if pilih_status != "Semua Status" and st_audit != pilih_status:
        continue
    if cari_batch.strip() and cari_batch.strip().lower() not in p["id_batch"].lower():
        continue
    paspor_terfilter.append(p)

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Ringkasan & Daftar Batch",
    "🔥 Analisis Sebaran Emisi",
    "📋 Daftar Faktor Emisi",
    "📱 Detail Rantai & Unduh QR Paspor",
])

with tab1:
    if not paspor_terfilter:
        st.warning("Tidak ada batch yang cocok dengan filter ini.")
    else:
        k1, k2, k3, k4 = st.columns(4)
        rata_emisi = sum(p["ringkasan_karbon"]["emisi_per_200g_kg"] for p in paspor_terfilter) / len(paspor_terfilter)
        rata_skor = sum(p["ringkasan_karbon"]["audit"]["skor_kelengkapan_persen"] for p in paspor_terfilter) / len(paspor_terfilter)
        total_pouch = sum(p["ringkasan_karbon"]["jumlah_pouch_200g"] for p in paspor_terfilter)

        k1.metric("Jumlah Batch Terpilih", f"{len(paspor_terfilter)} Batch")
        k2.metric("Total Kemasan 200 g", f"{total_pouch:,} Pouch")
        k3.metric("Rata-rata Jejak Karbon", f"{rata_emisi:.3f} kg CO₂e / 200g")
        k4.metric("Kelengkapan Data Rantai", f"{rata_skor:.1f}%")

        tabel_ringkas = []
        for p in paspor_terfilter:
            rk = p["ringkasan_karbon"]
            tabel_ringkas.append({
                "ID Batch": p["id_batch"],
                "Asal Kebun": p["rantai_pasok"]["kebun"].get("kecamatan"),
                "Varietas": p["rantai_pasok"]["kebun"].get("varietas"),
                "Skor Cupping": p["rantai_pasok"]["green_bean"].get("skor_cupping"),
                "Jumlah Kemasan (200g)": rk["jumlah_pouch_200g"],
                "Total Emisi Batch (kg CO₂e)": rk["total_emisi_batch_kg"],
                "Emisi per 200g (kg CO₂e)": rk["emisi_per_200g_kg"],
                "Kelengkapan (%)": rk["audit"]["skor_kelengkapan_persen"],
                "Status Data": rk["audit"]["status_audit"],
            })
        st.dataframe(pd.DataFrame(tabel_ringkas), use_container_width=True, hide_index=True)

with tab2:
    if not paspor_terfilter:
        st.warning("Pilih setidaknya satu batch untuk melihat grafik sebaran emisi.")
    else:
        c_chart1, c_chart2 = st.columns([1.3, 1])
        with c_chart1:
            rows_stack = []
            for p in paspor_terfilter:
                for thp, nilai in p["ringkasan_karbon"]["rincian_tahap"].items():
                    rows_stack.append({
                        "ID Batch": p["id_batch"],
                        "Tahap": thp.replace("_", " ").title(),
                        "Emisi (kg CO2e)": nilai,
                    })
            fig_bar = px.bar(
                pd.DataFrame(rows_stack),
                x="ID Batch",
                y="Emisi (kg CO2e)",
                color="Tahap",
                title="Rincian Jejak Karbon per Tahap Rantai Pasok (kg CO₂e / Batch)",
                barmode="stack",
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with c_chart2:
            komponen_total = {}
            for p in paspor_terfilter:
                for komp, val in p["ringkasan_karbon"]["rincian_komponen"].items():
                    komponen_total[komp] = komponen_total.get(komp, 0.0) + val
            df_pie = pd.DataFrame({
                "Sumber Aktivitas": list(komponen_total.keys()),
                "Total Emisi (kg CO2e)": list(komponen_total.values()),
            })
            fig_pie = px.pie(
                df_pie,
                names="Sumber Aktivitas",
                values="Total Emisi (kg CO2e)",
                hole=0.45,
                title="Proporsi Sumber Jejak Karbon",
            )
            st.plotly_chart(fig_pie, use_container_width=True)

with tab3:
    st.markdown("Berikut adalah daftar faktor konversi emisi yang digunakan dalam perhitungan setiap tahap:")
    st.dataframe(df_fe, use_container_width=True, hide_index=True)

with tab4:
    id_pilihan = st.selectbox(
        "Pilih ID Batch Kemasan 200 g untuk Melihat Paspor & Mengunduh QR:",
        [p["id_batch"] for p in daftar_paspor],
    )
    batch_aktif = next(p for p in daftar_paspor if p["id_batch"] == id_pilihan)
    rk_aktif = batch_aktif["ringkasan_karbon"]
    rp_aktif = batch_aktif["rantai_pasok"]

    col_pas1, col_pas2 = st.columns([2, 1])
    with col_pas1:
        st.markdown(f"#### Riwayat 7 Tahap Perjalanan Kopi — `{id_pilihan}`")
        if rk_aktif["audit"]["field_kosong"]:
            st.warning(f"Catatan kelengkapan: Terdapat data yang belum terisi pada {', '.join(rk_aktif['audit']['field_kosong'])}.")
        tahap_info = [
            ("1. Kebun Kopi", rp_aktif["kebun"], rk_aktif["rincian_tahap"]["kebun"]),
            ("2. Lot Panen", rp_aktif["lot_panen"], rk_aktif["rincian_tahap"]["lot_panen"]),
            ("3. Pascapanen Natural", rp_aktif["pascapanen"], rk_aktif["rincian_tahap"]["pascapanen"]),
            ("4. Lot Green Bean", rp_aktif["green_bean"], rk_aktif["rincian_tahap"]["green_bean"]),
            ("5. Batch Roasting", rp_aktif["roasting"], rk_aktif["rincian_tahap"]["roasting"]),
            ("6. Kemasan Produk Jadi (200 g)", rp_aktif["barang_jadi"], rk_aktif["rincian_tahap"]["barang_jadi"]),
            ("7. Distribusi", rp_aktif["distribusi"], rk_aktif["rincian_tahap"]["distribusi"]),
        ]
        for judul_thp, detail_dict, emisi_thp in tahap_info:
            with st.expander(f"{judul_thp} — Emisi Tahap: {emisi_thp:.2f} kg CO₂e", expanded=False):
                st.json(detail_dict)

    with col_pas2:
        st.markdown("#### QR Digital Passport")
        ringkasan_qr = (
            f"AGROTRACE PASSPORT\n"
            f"Batch: {id_pilihan}\n"
            f"Produk: Kopi Arabika Gayo Natural 200g\n"
            f"Kebun: {rp_aktif['kebun'].get('kecamatan')}\n"
            f"Emisi: {rk_aktif['emisi_per_200g_kg']:.3f} kg CO2e / 200g\n"
            f"Status: {rk_aktif['audit']['status_audit']}"
        )
        qr_png = buat_qr_bytes(ringkasan_qr)
        st.image(qr_png, caption=f"QR Paspor {id_pilihan}", width=220)
        st.download_button(
            label=f"⬇️ Unduh QR Code ({id_pilihan}.png)",
            data=qr_png,
            file_name=f"qr_{id_pilihan}.png",
            mime="image/png",
            use_container_width=True,
        )
