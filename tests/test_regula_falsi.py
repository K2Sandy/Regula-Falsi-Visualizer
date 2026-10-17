"""Tes inti algoritma Regula Falsi (tanpa parsing teks)."""

import math

import pytest

from regula_falsi import HasilRegulaFalsi, _hitung_error, regula_falsi


def kubik(x):
    return x**3 - x - 2


def test_akar_polinomial_kubik():
    hasil = regula_falsi(kubik, 1, 2, tol=1e-6, max_iter=200)
    assert hasil.konvergen
    assert hasil.akar == pytest.approx(1.5213797, abs=1e-5)
    assert abs(kubik(hasil.akar)) < 1e-4


def test_akar_fungsi_transenden():
    hasil = regula_falsi(lambda x: math.cos(x) - x, 0, 1, tol=1e-8, max_iter=200)
    assert hasil.konvergen
    assert hasil.akar == pytest.approx(0.7390851, abs=1e-6)


def test_akar_eksponensial():
    hasil = regula_falsi(lambda x: math.exp(x) - 3, 0, 2, tol=1e-8, max_iter=200)
    assert hasil.akar == pytest.approx(math.log(3), abs=1e-6)


def test_hasil_bertipe_dataclass():
    hasil = regula_falsi(kubik, 1, 2)
    assert isinstance(hasil, HasilRegulaFalsi)
    assert hasil.iterasi == len(hasil.tabel)


def test_tabel_iterasi_berisi_kolom_lengkap():
    hasil = regula_falsi(kubik, 1, 2, tol=1e-4)
    kolom = {"Iterasi", "a", "b", "c", "f(a)", "f(b)", "f(c)", "Error"}
    assert hasil.tabel
    for baris in hasil.tabel:
        assert set(baris) == kolom


def test_nomor_iterasi_berurutan_dari_satu():
    hasil = regula_falsi(kubik, 1, 2, tol=1e-4)
    assert [baris["Iterasi"] for baris in hasil.tabel] == list(range(1, hasil.iterasi + 1))


def test_error_iterasi_pertama_kosong():
    hasil = regula_falsi(kubik, 1, 2, tol=1e-4)
    assert hasil.tabel[0]["Error"] is None
    assert all(baris["Error"] is not None for baris in hasil.tabel[1:])


def test_titik_c_sesuai_rumus_regula_falsi():
    hasil = regula_falsi(kubik, 1, 2, tol=1e-4)
    baris = hasil.tabel[0]
    a, b, fa, fb = baris["a"], baris["b"], baris["f(a)"], baris["f(b)"]
    assert baris["c"] == pytest.approx((a * fb - b * fa) / (fb - fa))
    assert baris["f(c)"] == pytest.approx(kubik(baris["c"]))


def test_interval_selalu_mengurung_akar():
    hasil = regula_falsi(kubik, 1, 2, tol=1e-6, max_iter=200)
    for baris in hasil.tabel:
        assert baris["f(a)"] * baris["f(b)"] < 0


def test_error_akhir_di_bawah_toleransi_saat_konvergen():
    tol = 1e-5
    hasil = regula_falsi(kubik, 1, 2, tol=tol, max_iter=200)
    assert hasil.konvergen
    assert hasil.error < tol


def test_toleransi_lebih_kecil_butuh_iterasi_lebih_banyak():
    longgar = regula_falsi(kubik, 1, 2, tol=1e-2, max_iter=500)
    ketat = regula_falsi(kubik, 1, 2, tol=1e-8, max_iter=500)
    assert ketat.iterasi > longgar.iterasi


def test_iterasi_maksimum_tercapai():
    hasil = regula_falsi(kubik, 1, 2, tol=1e-12, max_iter=3)
    assert not hasil.konvergen
    assert hasil.iterasi == 3
    assert len(hasil.tabel) == 3
    assert "maksimum" in hasil.alasan.lower()


def test_akar_negatif():
    hasil = regula_falsi(lambda x: x**3 + 2, -2, 0, tol=1e-8, max_iter=200)
    assert hasil.akar == pytest.approx(-(2 ** (1 / 3)), abs=1e-6)


def test_akar_dekat_nol_tidak_bagi_nol():
    hasil = regula_falsi(lambda x: x, -1, 2, tol=1e-9, max_iter=50)
    assert hasil.konvergen
    assert hasil.akar == pytest.approx(0.0, abs=1e-9)


def test_hitung_error_iterasi_pertama_kosong():
    assert _hitung_error(1.5, None, 1e-6) is None


def test_hitung_error_relatif():
    assert _hitung_error(2.0, 1.0, 1e-6) == pytest.approx(0.5)


def test_hitung_error_absolut_saat_akar_dekat_nol():
    # |c| <= tol, jadi tidak boleh bagi dengan c
    assert _hitung_error(0.0, 1e-3, 1e-6) == pytest.approx(1e-3)
