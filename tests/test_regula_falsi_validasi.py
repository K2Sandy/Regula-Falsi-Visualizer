"""Tes validasi input dan kasus khusus pada regula_falsi."""

import pytest

from regula_falsi import regula_falsi


def kubik(x):
    return x**3 - x - 2


def test_batas_bawah_harus_lebih_kecil():
    with pytest.raises(ValueError, match="lebih kecil"):
        regula_falsi(kubik, 2, 1)


def test_batas_sama_ditolak():
    with pytest.raises(ValueError, match="lebih kecil"):
        regula_falsi(kubik, 1, 1)


@pytest.mark.parametrize("tol", [0, -1e-3])
def test_toleransi_harus_positif(tol):
    with pytest.raises(ValueError, match="Toleransi"):
        regula_falsi(kubik, 1, 2, tol=tol)


@pytest.mark.parametrize("max_iter", [0, -5])
def test_iterasi_maksimum_minimal_satu(max_iter):
    with pytest.raises(ValueError, match="Iterasi maksimum"):
        regula_falsi(kubik, 1, 2, max_iter=max_iter)


def test_tanda_sama_ditolak_dengan_pesan_jelas():
    with pytest.raises(ValueError, match="berbeda tanda") as info:
        regula_falsi(kubik, 2, 3)
    assert "f(2)" in str(info.value)
    assert "f(3)" in str(info.value)


def test_akar_di_batas_bawah():
    hasil = regula_falsi(lambda x: x - 1, 1, 3)
    assert hasil.akar == 1
    assert hasil.iterasi == 0
    assert hasil.konvergen
    assert hasil.error == 0.0
    assert hasil.tabel == []


def test_akar_di_batas_atas():
    hasil = regula_falsi(lambda x: x - 3, 1, 3)
    assert hasil.akar == 3
    assert hasil.iterasi == 0
    assert hasil.konvergen


def test_fungsi_linear_selesai_satu_iterasi():
    hasil = regula_falsi(lambda x: 2 * x - 5, 0, 10, tol=1e-6)
    assert hasil.akar == pytest.approx(2.5)
    assert hasil.konvergen
    assert hasil.error == 0.0
    assert hasil.iterasi == 1


def test_galat_dari_fungsi_diteruskan():
    def rusak(x):
        raise ValueError("f(x) tidak terdefinisi")

    with pytest.raises(ValueError, match="tidak terdefinisi"):
        regula_falsi(rusak, 1, 2)
