"""Tes cari_interval: mencari selang yang mengurung akar."""

import math

import pytest

from interval import cari_interval
from parsing import parse_fungsi
from regula_falsi import regula_falsi


def test_satu_akar_kubik():
    hasil = cari_interval(lambda x: x**3 - x - 2)
    assert len(hasil) == 1
    a, b = hasil[0]
    assert a < 1.5213797 < b


def test_tiga_akar_urut_dari_kiri():
    hasil = cari_interval(lambda x: (x + 3) * (x - 1) * (x - 4.5))
    assert len(hasil) == 3
    for (a, b), akar in zip(hasil, (-3, 1, 4.5), strict=True):
        assert a <= akar <= b


def test_tiap_selang_lolos_syarat_regula_falsi():
    f = parse_fungsi("sin(x) - 0.3")
    for a, b in cari_interval(f, -5, 5):
        hasil = regula_falsi(f, a, b, tol=1e-8, max_iter=200)
        assert math.sin(hasil.akar) == pytest.approx(0.3, abs=1e-6)


def test_tanpa_akar_mengembalikan_daftar_kosong():
    assert cari_interval(lambda x: x**2 + 1) == []


def test_kutub_tidak_dianggap_akar():
    # 1/x berganti tanda di x = 0 tapi tidak punya akar
    assert cari_interval(parse_fungsi("1/x"), -1, 1, potongan=7) == []


def test_tan_hanya_akar_bukan_kutub():
    hasil = cari_interval(math.tan, -2, 2, potongan=41)
    assert len(hasil) == 1
    a, b = hasil[0]
    assert a <= 0 <= b


def test_titik_di_luar_domain_dilewati():
    hasil = cari_interval(parse_fungsi("ln(x) - 1"), -5, 5)
    assert len(hasil) == 1
    a, b = hasil[0]
    assert a < math.e < b


def test_akar_tepat_di_titik_grid():
    hasil = cari_interval(lambda x: x**2, -1, 1, potongan=4)
    assert hasil == [(0.0, 0.5)]


def test_akar_tepat_di_ujung_kanan_rentang():
    assert cari_interval(lambda x: x - 2, 0, 2, potongan=4) == [(1.5, 2.0)]


def test_jumlah_selang_dibatasi():
    hasil = cari_interval(math.sin, -50, 50, potongan=1000, maksimum=3)
    assert len(hasil) == 3


def test_batas_selang_bersih_dari_galat_pembulatan():
    for a, b in cari_interval(lambda x: x - 0.3, 0, 1, potongan=10):
        assert (a, b) == (0.3, 0.4)


@pytest.mark.parametrize(
    "awal, akhir, potongan",
    [(1, 1, 10), (2, 1, 10), (float("nan"), 1, 10), (0, float("inf"), 10), (0, 1, 0)],
)
def test_input_tidak_valid_ditolak(awal, akhir, potongan):
    with pytest.raises(ValueError):
        cari_interval(lambda x: x, awal, akhir, potongan)
