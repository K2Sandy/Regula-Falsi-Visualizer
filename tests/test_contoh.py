"""Tes contoh soal: tiap contoh harus valid dan konvergen."""

import pytest

from contoh import DAFTAR_CONTOH, ContohSoal, cari_contoh
from parsing import parse_fungsi
from regula_falsi import regula_falsi


@pytest.mark.parametrize("contoh", DAFTAR_CONTOH, ids=lambda c: c.nama)
def test_contoh_konvergen_ke_akar_sebenarnya(contoh: ContohSoal):
    f = parse_fungsi(contoh.fungsi)
    hasil = regula_falsi(f, contoh.a, contoh.b, contoh.tol, contoh.max_iter)
    assert hasil.konvergen
    assert hasil.akar == pytest.approx(contoh.akar, abs=1e-3)


@pytest.mark.parametrize("contoh", DAFTAR_CONTOH, ids=lambda c: c.nama)
def test_akar_ada_di_dalam_interval(contoh: ContohSoal):
    assert contoh.a < contoh.akar < contoh.b


def test_nama_contoh_unik():
    nama = [contoh.nama for contoh in DAFTAR_CONTOH]
    assert len(nama) == len(set(nama))


def test_kasus_lambat_memang_butuh_banyak_iterasi():
    contoh = cari_contoh("Kasus lambat: x^10 - 1")
    hasil = regula_falsi(parse_fungsi(contoh.fungsi), contoh.a, contoh.b, contoh.tol, contoh.max_iter)
    assert hasil.iterasi > 30
    assert {baris["b"] for baris in hasil.tabel} == {1.3}


def test_cari_contoh_berdasarkan_nama():
    assert cari_contoh("Polinomial kubik").fungsi == "x^3 - x - 2"


def test_cari_contoh_tidak_ada():
    with pytest.raises(KeyError):
        cari_contoh("tidak ada")
