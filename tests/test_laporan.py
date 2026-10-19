"""Tes laporan: penjelasan iterasi dan ekspor tabel."""

import math

import pytest

from laporan import jelaskan_iterasi, tabel_ke_csv, tabel_ke_dataframe
from regula_falsi import regula_falsi


def kubik(x):
    return x**3 - x - 2


@pytest.fixture
def hasil_kubik():
    return regula_falsi(kubik, 1, 2, tol=1e-4)


def test_iterasi_pertama_menyebut_titik_dan_error_kosong(hasil_kubik):
    teks = " ".join(jelaskan_iterasi(hasil_kubik, 1, 1e-4))
    assert "(1, -2)" in teks
    assert "(2, 4)" in teks
    assert "c = 1.33333" in teks
    assert "error belum bisa dihitung" in teks


def test_akar_di_kanan_c_maka_a_diganti(hasil_kubik):
    # f(1.333) < 0 dan f(1) < 0 bertanda sama, jadi a = c
    teks = " ".join(jelaskan_iterasi(hasil_kubik, 1, 1e-4))
    assert "a diganti dengan c" in teks


def test_akar_di_kiri_c_maka_b_diganti():
    # f(0) = -1, f(4) = 1, c = 2, f(2) = 0.41 berbeda tanda dengan f(a), jadi b = c
    hasil = regula_falsi(lambda x: x**0.5 - 1, 0, 4, tol=1e-4)
    teks = " ".join(jelaskan_iterasi(hasil, 1, 1e-4))
    assert "b diganti dengan c" in teks


def test_iterasi_tengah_error_masih_besar(hasil_kubik):
    teks = " ".join(jelaskan_iterasi(hasil_kubik, 2, 1e-4))
    assert "masih lebih besar dari toleransi" in teks


def test_iterasi_terakhir_menyebut_alasan_berhenti(hasil_kubik):
    teks = " ".join(jelaskan_iterasi(hasil_kubik, hasil_kubik.iterasi, 1e-4))
    assert "sudah lebih kecil dari toleransi" in teks
    assert "Iterasi berhenti di sini" in teks
    assert hasil_kubik.alasan in teks


def test_iterasi_terakhir_saat_belum_konvergen():
    hasil = regula_falsi(kubik, 1, 2, tol=1e-12, max_iter=3)
    teks = " ".join(jelaskan_iterasi(hasil, 3, 1e-12))
    assert "Iterasi maksimum tercapai" in teks


@pytest.mark.parametrize("nomor", [0, -1, 99])
def test_nomor_iterasi_di_luar_tabel_ditolak(hasil_kubik, nomor):
    with pytest.raises(ValueError, match="tidak ada"):
        jelaskan_iterasi(hasil_kubik, nomor, 1e-4)


# ---------- tabel_ke_dataframe & tabel_ke_csv ----------


def test_dataframe_kolom_dan_jumlah_baris(hasil_kubik):
    df = tabel_ke_dataframe(hasil_kubik)
    assert list(df.columns) == ["Iterasi", "a", "b", "c", "f(a)", "f(b)", "f(c)", "Error"]
    assert len(df) == hasil_kubik.iterasi


def test_dataframe_error_pertama_nan_dan_kolom_angka(hasil_kubik):
    df = tabel_ke_dataframe(hasil_kubik)
    assert math.isnan(df["Error"].iloc[0])
    assert df["Error"].dtype.kind == "f"


def test_dataframe_kosong_saat_akar_di_ujung_interval():
    hasil = regula_falsi(lambda x: x - 1, 1, 2)
    df = tabel_ke_dataframe(hasil)
    assert df.empty
    assert "Iterasi" in df.columns


def test_csv_berisi_header_dan_semua_baris(hasil_kubik):
    teks = tabel_ke_csv(hasil_kubik).decode("utf-8")
    baris = teks.strip().splitlines()
    assert baris[0] == "Iterasi,a,b,c,f(a),f(b),f(c),Error"
    assert len(baris) == hasil_kubik.iterasi + 1


def test_csv_error_pertama_kosong_dan_angka_12_digit(hasil_kubik):
    baris = tabel_ke_csv(hasil_kubik).decode("utf-8").splitlines()
    pertama = baris[1].split(",")
    assert pertama[0] == "1"
    assert pertama[-1] == ""
    assert pertama[3] == "1.33333333333"
