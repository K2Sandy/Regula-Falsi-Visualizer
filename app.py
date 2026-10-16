"""Kalkulator Persamaan Nonlinier - Metode Regula Falsi.

Jalankan dengan:  streamlit run app.py
"""

import pandas as pd
import streamlit as st

from grafik import buat_grafik
from parsing import parse_fungsi
from regula_falsi import regula_falsi

st.set_page_config(page_title="Kalkulator Regula Falsi", page_icon="📈", layout="wide")

st.title("📈 Kalkulator Regula Falsi")
st.caption("Mencari akar persamaan nonlinier f(x) = 0 dengan Metode Regula Falsi")

# ---------- input ----------
st.subheader("Input")

f_teks = st.text_input(
    "Fungsi f(x)",
    value="",
    placeholder="Contoh: x^3 - x - 2   atau   e^x - 3 = 0",
    help="Contoh: x^3 - x - 2, cos(x) - x, exp(x) - 3*x, e^x - 3. Boleh pakai '= 0'.",
)

kol1, kol2, kol3, kol4 = st.columns(4)
a = kol1.number_input("Batas bawah (a)", value=None, placeholder="Contoh: 1", format="%g")
b = kol2.number_input("Batas atas (b)", value=None, placeholder="Contoh: 2", format="%g")
tol = kol3.number_input("Toleransi error", value=None, min_value=0.0, placeholder="Contoh: 0.0001", format="%g")
max_iter = kol4.number_input("Iterasi maksimum", value=None, min_value=1, step=1, placeholder="Contoh: 100")

hitung = st.button("Hitung", type="primary")

# ---------- proses & hasil ----------
if hitung:
    if not f_teks.strip() or None in (a, b, tol, max_iter):
        st.warning("Lengkapi semua isian: fungsi, batas bawah, batas atas, toleransi, dan iterasi maksimum.")
        st.stop()

    try:
        f = parse_fungsi(f_teks)
        hasil = regula_falsi(f, a, b, tol, int(max_iter))
    except ValueError as e:
        st.error(str(e))
    else:
        st.subheader("Hasil")

        m1, m2, m3 = st.columns(3)
        m1.metric("Akar", f"{hasil.akar:.8g}")
        m2.metric("Jumlah iterasi", hasil.iterasi)
        m3.metric(
            "Error akhir",
            "-" if hasil.error is None else f"{hasil.error:.3e}",
        )

        if hasil.konvergen:
            st.success(hasil.alasan)
        else:
            st.warning(hasil.alasan)

        kiri, kanan = st.columns(2)

        with kiri:
            st.subheader("Tabel iterasi")
            if hasil.tabel:
                st.dataframe(pd.DataFrame(hasil.tabel), hide_index=True)
            else:
                st.info("Tidak ada iterasi, akar sudah ada di ujung interval.")

        with kanan:
            st.subheader("Grafik")
            st.pyplot(buat_grafik(f, a, b, hasil))