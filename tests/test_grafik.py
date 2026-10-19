"""Tes buat_grafik: pastikan figure terbentuk dan berisi data yang benar."""

import math

import numpy as np
import pytest
from matplotlib.figure import Figure

from grafik import buat_grafik
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
