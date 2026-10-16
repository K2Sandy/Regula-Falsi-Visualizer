"""Tes parse_fungsi: teks f(x) jadi fungsi Python."""

import math

import pytest

from parsing import parse_fungsi


@pytest.mark.parametrize(
    "teks, x, diharapkan",
    [
        ("x^3 - x - 2", 2, 4),
        ("x**2 + 1", 3, 10),
        ("2x + 1", 4, 9),
        ("3*x - 6", 2, 0),
        ("cos(x) - x", 0, 1),
        ("exp(x) - 3*x", 0, 1),
        ("sqrt(x) - 2", 9, 1),
        ("abs(x) - 5", -7, 2),
        ("1/x - 2", 4, -1.75),
        ("(x - 1)(x + 1)", 3, 8),
    ],
)
def test_ekspresi_umum(teks, x, diharapkan):
    assert parse_fungsi(teks)(x) == pytest.approx(diharapkan)


def test_e_dibaca_sebagai_bilangan_euler():
    f = parse_fungsi("e^x - 3")
    assert f(0) == pytest.approx(-2)
    assert f(math.log(3)) == pytest.approx(0, abs=1e-12)


def test_pi_dibaca_sebagai_konstanta():
    assert parse_fungsi("sin(x) + pi")(0) == pytest.approx(math.pi)


def test_ln_adalah_logaritma_natural():
    assert parse_fungsi("ln(x)")(math.e) == pytest.approx(1)


def test_spasi_berlebih_tidak_masalah():
    assert parse_fungsi("   x   ^  2  -  4   ")(3) == pytest.approx(5)


def test_persamaan_dengan_tanda_sama_dengan_nol():
    f = parse_fungsi("x^3 - x - 1 = 0")
    assert f(2) == pytest.approx(5)


def test_sisi_kanan_dipindahkan_ke_kiri():
    f = parse_fungsi("e^x = 3")
    assert f(0) == pytest.approx(-2)
    assert f(math.log(3)) == pytest.approx(0, abs=1e-12)


def test_hasil_selalu_float():
    assert isinstance(parse_fungsi("x^2")(3), float)


@pytest.mark.parametrize("teks", ["", "   ", None])
def test_teks_kosong_ditolak(teks):
    with pytest.raises(ValueError, match="belum diisi"):
        parse_fungsi(teks)


@pytest.mark.parametrize("teks", ["x +", "x ^^ 2", "((x)", "x = = 2", "= 3", "x = ", "1 = 2 = 3"])
def test_sintaks_salah_ditolak(teks):
    with pytest.raises(ValueError):
        parse_fungsi(teks)


def test_variabel_selain_x_ditolak():
    with pytest.raises(ValueError, match="variabel x"):
        parse_fungsi("y^2 - 1")


def test_dunder_ditolak():
    with pytest.raises(ValueError, match="tidak diizinkan"):
        parse_fungsi("x.__class__")


def test_log_negatif_memberi_error_jelas():
    f = parse_fungsi("log(x)")
    with pytest.raises(ValueError, match="x = -1"):
        f(-1)


def test_pembagian_nol_memberi_error_jelas():
    f = parse_fungsi("1/x")
    with pytest.raises(ValueError, match="x = 0"):
        f(0)
