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


# ---------- keamanan input ----------


@pytest.mark.parametrize(
    "teks",
    [
        "exec('x=1')",
        "open('data.txt')",
        "__import__('os')",
        "eval('1+1')",
        "x; x",
        "x[0]",
        "lambda: 1",
        "x'1'",
        "x@x",
        "x.real",
        "{x}",
    ],
)
def test_teks_berbahaya_ditolak(teks):
    with pytest.raises(ValueError):
        parse_fungsi(teks)


def test_exec_tidak_dijalankan(tmp_path):
    berkas = tmp_path / "bukti.txt"
    teks = f"exec(\"open('{berkas}','w').write('x')\")"
    with pytest.raises(ValueError):
        parse_fungsi(teks)
    assert not berkas.exists()


def test_nama_tidak_dikenal_disebut_di_pesan_error():
    with pytest.raises(ValueError, match="'foo'"):
        parse_fungsi("foo(x)")


def test_teks_terlalu_panjang_ditolak():
    with pytest.raises(ValueError, match="terlalu panjang"):
        parse_fungsi("x + " * 100 + "1")


@pytest.mark.parametrize("teks", ["9^9^9^9 + x", "9**9**9**9 + x", "cos(9^9^9^9) + x", "e^x = 9^9^9^9"])
def test_menara_pangkat_tidak_membuat_macet(teks):
    f = parse_fungsi(teks)          # harus selesai cepat
    with pytest.raises(ValueError):
        f(2.0)                      # terlalu besar, bukan hang


@pytest.mark.parametrize("teks, x", [("2e-3*x", 1), ("1e3 - x", 1), ("x^0.5", 4), ("2pi*x", 1)])
def test_angka_ilmiah_dan_desimal_tetap_valid(teks, x):
    assert isinstance(parse_fungsi(teks)(x), float)


def test_gabungan_konstanta_tanpa_spasi():
    assert parse_fungsi("xe")(2) == pytest.approx(2 * math.e)


# ---------- logaritma basis 10 dan 2 ----------


@pytest.mark.parametrize("teks, x, diharapkan", [("log10(x)", 1000, 3), ("log2(x)", 8, 3), ("log10(x) - 2", 100, 0)])
def test_logaritma_basis_10_dan_2(teks, x, diharapkan):
    assert parse_fungsi(teks)(x) == pytest.approx(diharapkan)


def test_log_biasa_tetap_logaritma_natural():
    assert parse_fungsi("log(x)")(math.e) == pytest.approx(1)


def test_logaritma_dalam_persamaan():
    f = parse_fungsi("log10(x) = 2")
    assert f(100) == pytest.approx(0)


def test_nama_dengan_angka_yang_tidak_dikenal_ditolak():
    with pytest.raises(ValueError, match="'x2'"):
        parse_fungsi("x2 + 1")


# ---------- simbol unicode hasil salin-tempel ----------


@pytest.mark.parametrize(
    "teks, x, diharapkan",
    [
        ("x² − 4", 3, 5),
        ("x³ − x − 2", 2, 4),
        ("2 × x + 1", 4, 9),
        ("2·x + 1", 4, 9),
        ("x ÷ 2", 6, 3),
        ("x − π", 0, -math.pi),
        ("√x − 2", 9, 1),
        ("√(x) − 2", 16, 2),
        ("x – 1", 3, 2),
    ],
)
def test_simbol_unicode_dinormalkan(teks, x, diharapkan):
    assert parse_fungsi(teks)(x) == pytest.approx(diharapkan)


def test_persamaan_dengan_simbol_unicode():
    assert parse_fungsi("x² = 4")(3) == pytest.approx(5)
