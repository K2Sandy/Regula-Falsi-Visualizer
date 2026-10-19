"""Tes buat_grafik: pastikan figure terbentuk dan berisi data yang benar."""

import math

import numpy as np
import pytest
from matplotlib.figure import Figure

from grafik import buat_grafik, buat_grafik_iterasi, buat_grafik_konvergensi
from parsing import parse_fungsi
from regula_falsi import regula_falsi


def test_mengembalikan_figure():
    fig = buat_grafik(lambda x: x**2 - 2, 0, 2)
    assert isinstance(fig, Figure)


def test_kurva_dan_garis_batas_tergambar():
    fig = buat_grafik(lambda x: x**2 - 2, 0, 2)
    ax = fig.axes[0]
    labels = [teks.get_text() for teks in ax.get_legend().get_texts()]
    assert "f(x)" in labels
    assert "a = 0" in labels
    assert "b = 2" in labels


def test_tanpa_hasil_tidak_ada_penanda_akar():
    fig = buat_grafik(lambda x: x**2 - 2, 0, 2)
    labels = [teks.get_text() for teks in fig.axes[0].get_legend().get_texts()]
    assert not any(label.startswith("akar") for label in labels)


def test_akar_ditandai_saat_hasil_diberikan():
    f = parse_fungsi("x^2 - 2")
    hasil = regula_falsi(f, 0, 2, tol=1e-8, max_iter=200)
    fig = buat_grafik(f, 0, 2, hasil)
    labels = [teks.get_text() for teks in fig.axes[0].get_legend().get_texts()]
    assert any(label.startswith("akar") for label in labels)


def test_rentang_x_melebihi_interval_seperempat_lebar():
    fig = buat_grafik(lambda x: x, 0, 4)
    garis = fig.axes[0].lines[0]
    xs = garis.get_xdata()
    assert math.isclose(xs[0], -1.0)
    assert math.isclose(xs[-1], 5.0)
    assert len(xs) == 400


def test_titik_di_luar_domain_menjadi_nan():
    f = parse_fungsi("log(x)")
    fig = buat_grafik(f, -1, 2)
    ys = np.asarray(fig.axes[0].lines[0].get_ydata(), dtype=float)
    xs = np.asarray(fig.axes[0].lines[0].get_xdata(), dtype=float)
    di_luar_domain = xs <= 0
    assert di_luar_domain.any()
    assert np.isnan(ys[di_luar_domain]).all()
    assert np.isfinite(ys[~di_luar_domain]).all()


def test_interval_diarsir():
    fig = buat_grafik(lambda x: x**2 - 2, 0, 2)
    assert len(fig.axes[0].patches) == 1


def test_kurva_diputus_di_kutub():
    f = parse_fungsi("1/(x - 1) - 2")
    fig = buat_grafik(f, 0.5, 2)
    xs = np.asarray(fig.axes[0].lines[0].get_xdata(), dtype=float)
    ys = np.asarray(fig.axes[0].lines[0].get_ydata(), dtype=float)
    putus = xs[np.isnan(ys)]
    assert len(putus) == 1
    assert putus[0] == pytest.approx(1, abs=0.01)


def test_sumbu_y_dipotong_di_sekitar_kutub():
    fig = buat_grafik(parse_fungsi("1/(x - 1) - 2"), 0.5, 2)
    bawah, atas = fig.axes[0].get_ylim()
    assert atas - bawah < 200


def test_kurva_mulus_tidak_diputus():
    fig = buat_grafik(parse_fungsi("e^x - 3"), 0, 2)
    ys = np.asarray(fig.axes[0].lines[0].get_ydata(), dtype=float)
    assert np.isfinite(ys).all()


# ---------- buat_grafik_iterasi ----------


def _label(fig):
    return [teks.get_text() for teks in fig.axes[0].get_legend().get_texts()]


def _hasil_kubik():
    f = parse_fungsi("x^3 - x - 2")
    return f, regula_falsi(f, 1, 2, tol=1e-4)


def test_iterasi_pertama_tanpa_jejak_c():
    f, hasil = _hasil_kubik()
    fig = buat_grafik_iterasi(f, 1, 2, hasil, 1)
    label = _label(fig)
    assert "garis potong" in label
    assert "c = 1.33333" in label
    assert "c sebelumnya" not in label
    assert fig.axes[0].get_title(loc="left") == "Iterasi 1 dari 8"


def test_garis_potong_menghubungkan_a_dan_b_iterasi_itu():
    f, hasil = _hasil_kubik()
    fig = buat_grafik_iterasi(f, 1, 2, hasil, 3)
    baris = hasil.tabel[2]
    garis = next(g for g in fig.axes[0].lines if g.get_label() == "garis potong")
    assert list(garis.get_xdata()) == [baris["a"], baris["b"]]
    assert list(garis.get_ydata()) == [baris["f(a)"], baris["f(b)"]]


def test_jejak_c_sebelumnya_ikut_digambar():
    f, hasil = _hasil_kubik()
    fig = buat_grafik_iterasi(f, 1, 2, hasil, 4)
    jejak = next(g for g in fig.axes[0].lines if g.get_label() == "c sebelumnya")
    assert list(jejak.get_xdata()) == [baris["c"] for baris in hasil.tabel[:3]]


def test_skala_x_sama_di_semua_iterasi():
    f, hasil = _hasil_kubik()
    batas = {buat_grafik_iterasi(f, 1, 2, hasil, n).axes[0].lines[0].get_xdata()[0] for n in (1, 5, 8)}
    assert len(batas) == 1


@pytest.mark.parametrize("nomor", [0, 9])
def test_nomor_iterasi_di_luar_tabel_ditolak(nomor):
    f, hasil = _hasil_kubik()
    with pytest.raises(ValueError, match="tidak ada"):
        buat_grafik_iterasi(f, 1, 2, hasil, nomor)


# ---------- buat_grafik_konvergensi ----------


def test_konvergensi_skala_log_dengan_garis_toleransi():
    _, hasil = _hasil_kubik()
    fig = buat_grafik_konvergensi(hasil, 1e-4)
    ax = fig.axes[0]
    assert ax.get_yscale() == "log"
    assert "toleransi = 0.0001" in _label(fig)


def test_konvergensi_error_mulai_iterasi_kedua():
    _, hasil = _hasil_kubik()
    fig = buat_grafik_konvergensi(hasil, 1e-4)
    garis = next(g for g in fig.axes[0].lines if g.get_label() == "error relatif")
    assert list(garis.get_xdata()) == list(range(2, hasil.iterasi + 1))
    assert garis.get_ydata()[-1] < 1e-4


def test_konvergensi_tanpa_iterasi_menampilkan_pesan():
    hasil = regula_falsi(lambda x: x - 1, 1, 2)
    fig = buat_grafik_konvergensi(hasil, 1e-4)
    assert fig.axes[0].get_legend() is None
    assert "Tidak ada error" in fig.axes[0].texts[0].get_text()
