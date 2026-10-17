"""Tes alur lengkap: teks f(x) -> parse_fungsi -> regula_falsi -> buat_grafik.

Angka di sini sama dengan tabel contoh di README.md dan docs/algoritma.md,
jadi kalau algoritma berubah dan angkanya bergeser, dokumennya ikut dicek.
"""

import pytest
from matplotlib.figure import Figure

from grafik import buat_grafik
from parsing import parse_fungsi
from regula_falsi import regula_falsi


@pytest.mark.parametrize(
    "teks, a, b, akar, iterasi",
    [
        ("x^3 - x - 2", 1, 2, 1.5213, 8),
        ("cos(x) - x", 0, 1, 0.7391, 5),
        ("e^x - 3", 0, 2, 1.0986, 11),
    ],
)
def test_contoh_di_readme(teks, a, b, akar, iterasi):
    hasil = regula_falsi(parse_fungsi(teks), a, b, tol=1e-4, max_iter=100)
    assert hasil.konvergen
    assert hasil.iterasi == iterasi
    assert round(hasil.akar, 4) == akar


def test_tabel_contoh_di_docs_algoritma():
    hasil = regula_falsi(parse_fungsi("x^3 - x - 2"), 1, 2, tol=1e-4)
    pertama, terakhir = hasil.tabel[0], hasil.tabel[-1]
    assert pertama["c"] == pytest.approx(1.333333, abs=1e-6)
    assert pertama["f(c)"] == pytest.approx(-0.962963, abs=1e-6)
    assert terakhir["c"] == pytest.approx(1.521344, abs=1e-6)
    assert terakhir["Error"] == pytest.approx(5.70e-05, rel=1e-2)
    assert {baris["b"] for baris in hasil.tabel} == {2}   # ujung b macet di 2


@pytest.mark.parametrize("teks", ["e^x - 3", "e^x-3", "e^x = 3", "e^x - 3 = 0", "exp(x) = 3"])
def test_bentuk_penulisan_berbeda_hasil_sama(teks):
    hasil = regula_falsi(parse_fungsi(teks), 0, 2, tol=1e-8, max_iter=200)
    assert hasil.akar == pytest.approx(1.0986123, abs=1e-6)


def test_input_dengan_simbol_unicode_sampai_ke_hasil():
    hasil = regula_falsi(parse_fungsi("x³ − x − 2"), 1, 2, tol=1e-8, max_iter=200)
    assert hasil.akar == pytest.approx(1.5213797, abs=1e-6)


def test_interval_tanpa_akar_ditolak_dengan_nilai_f():
    f = parse_fungsi("x^2 + 1")
    with pytest.raises(ValueError, match="berbeda tanda") as info:
        regula_falsi(f, -1, 1)
    assert "f(-1) = 2" in str(info.value)


def test_fungsi_tak_terdefinisi_di_ujung_interval():
    f = parse_fungsi("log(x)")
    with pytest.raises(ValueError, match="x = -1"):
        regula_falsi(f, -1, 2)


def test_alur_sampai_grafik():
    f = parse_fungsi("cos(x) - x")
    hasil = regula_falsi(f, 0, 1, tol=1e-6)
    fig = buat_grafik(f, 0, 1, hasil)
    assert isinstance(fig, Figure)
    label = [t.get_text() for t in fig.axes[0].get_legend().get_texts()]
    assert any(teks.startswith("akar ≈ 0.7390") for teks in label)
