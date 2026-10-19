"""Kalkulator Persamaan Nonlinier - Metode Regula Falsi.

Jalankan dengan:  streamlit run app.py
"""

import pandas as pd
import streamlit as st

from contoh import DAFTAR_CONTOH, cari_contoh
from grafik import buat_grafik
from interval import cari_interval
from parsing import ke_latex, parse_fungsi
from regula_falsi import regula_falsi
from style import footer, judul, terapkan_gaya

st.set_page_config(page_title="Regula Falsi Visualizer", page_icon="📈", layout="wide")

terapkan_gaya()

judul()


def isi_contoh() -> None:
    """Isi semua input dari contoh soal yang dipilih."""
    nama = st.session_state.get("contoh")
    if not nama:
        return
    contoh = cari_contoh(nama)
    st.session_state.f_teks = contoh.fungsi
    st.session_state.a = float(contoh.a)
    st.session_state.b = float(contoh.b)
    st.session_state.tol = contoh.tol
    st.session_state.max_iter = contoh.max_iter


RENTANG_CARI = (-10.0, 10.0)


def isi_interval_otomatis() -> None:
    """Cari selang yang mengurung akar di RENTANG_CARI, lalu isi batas a dan b."""
    try:
        f = parse_fungsi(st.session_state.get("f_teks", ""))
    except ValueError as e:
        st.session_state.pesan_interval = ("error", str(e))
        return
    awal, akhir = RENTANG_CARI
    selang = cari_interval(f, awal, akhir)
    if not selang:
        st.session_state.pesan_interval = (
            "warning",
            f"Tidak ada perubahan tanda f(x) di rentang {awal:g} sampai {akhir:g}. "
            "Isi batas a dan b sendiri, atau periksa apakah fungsinya punya akar real.",
        )
        return
    st.session_state.a, st.session_state.b = selang[0]
    daftar = ", ".join(f"[{a:g}, {b:g}]" for a, b in selang)
    st.session_state.pesan_interval = (
        "info",
        f"Ditemukan {len(selang)} selang yang mengurung akar: {daftar}. "
        f"Batas a dan b diisi dengan selang pertama.",
    )


# ---------- input ----------
with st.container(key="kartu_input"):
    kiri, kanan = st.columns([3, 2], gap="medium")
    f_teks = kiri.text_input(
        "Fungsi f(x)",
        key="f_teks",
        placeholder="Contoh: x^3 - x - 2   atau   e^x = 3",
        help="Pakai x sebagai variabel. Boleh ^ untuk pangkat, 2x untuk 2*x, dan '= 0'. "
        "Fungsi: sin cos tan exp ln log10 sqrt abs, konstanta e dan pi.",
    )
    kanan.selectbox(
        "Contoh soal",
        options=[contoh.nama for contoh in DAFTAR_CONTOH],
        index=None,
        key="contoh",
        placeholder="Pilih untuk mengisi otomatis",
        on_change=isi_contoh,
    )

    # pratinjau: tampilkan rumus seperti yang dibaca aplikasi
    if f_teks.strip():
        try:
            rumus = ke_latex(f_teks)
        except ValueError as e:
            st.caption(f"⚠️ {e}")
        else:
            with st.container(key="pratinjau"):
                st.markdown(f"$f(x) = {rumus}$")
    if st.session_state.get("contoh"):
        st.caption(cari_contoh(st.session_state.contoh).catatan)

    kol1, kol2, kol3, kol4 = st.columns(4)
    a = kol1.number_input("Batas bawah (a)", value=None, key="a", placeholder="Contoh: 1", format="%g")
    b = kol2.number_input("Batas atas (b)", value=None, key="b", placeholder="Contoh: 2", format="%g")
    tol = kol3.number_input(
        "Toleransi error", value=None, key="tol", min_value=0.0, placeholder="Contoh: 0.0001", format="%g"
    )
    max_iter = kol4.number_input(
        "Iterasi maksimum", value=None, key="max_iter", min_value=1, step=1, placeholder="Contoh: 100"
    )

    tombol_kiri, tombol_kanan, _ = st.columns([1, 1, 3], gap="small")
    hitung = tombol_kiri.button("Hitung akar", type="primary", width="stretch")
    tombol_kanan.button(
        "Cari interval",
        on_click=isi_interval_otomatis,
        width="stretch",
        help="Cari selang [a, b] yang mengurung akar di rentang -10 sampai 10.",
    )

    if "pesan_interval" in st.session_state:
        jenis, pesan = st.session_state.pop("pesan_interval")
        {"error": st.error, "warning": st.warning, "info": st.info}[jenis](pesan)

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

footer()
