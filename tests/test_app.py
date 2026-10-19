"""Tes antarmuka Streamlit dengan AppTest (tanpa membuka browser)."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


@pytest.fixture
def at():
    app = AppTest.from_file(APP, default_timeout=30)
    app.run()
    assert not app.exception
    return app


def _tombol(at, label):
    return next(tombol for tombol in at.button if tombol.label == label)


def _isi(at, fungsi, a, b, tol=0.0001, max_iter=100):
    at.text_input(key="f_teks").set_value(fungsi)
    at.number_input(key="a").set_value(a)
    at.number_input(key="b").set_value(b)
    at.number_input(key="tol").set_value(tol)
    at.number_input(key="max_iter").set_value(max_iter)
    at.run()


def _semua_markdown(at):
    return " ".join(md.value for md in at.markdown)


def test_tampilan_awal_menunjukkan_petunjuk(at):
    assert "Belum ada hasil" in _semua_markdown(at)
    assert not at.metric


def test_pilih_contoh_mengisi_semua_input(at):
    at.selectbox(key="contoh").select("Polinomial kubik").run()
    assert at.text_input(key="f_teks").value == "x^3 - x - 2"
    assert at.number_input(key="a").value == 1
    assert at.number_input(key="b").value == 2
    assert at.number_input(key="tol").value == 0.0001
    assert at.number_input(key="max_iter").value == 100


def test_hitung_menampilkan_akar_dan_empat_tab(at):
    at.selectbox(key="contoh").select("Polinomial kubik").run()
    _tombol(at, "Hitung akar").click().run()
    assert not at.exception
    nilai = {m.label: m.value for m in at.metric}
    assert nilai["Akar"] == "1.5213445"
    assert nilai["Jumlah iterasi"] == "8"
    assert [tab.label for tab in at.tabs] == ["Langkah demi langkah", "Grafik", "Tabel iterasi", "Konvergensi"]
    assert at.success[0].value == "Error sudah lebih kecil dari toleransi."


def test_hasil_tetap_ada_saat_slider_digeser(at):
    at.selectbox(key="contoh").select("Polinomial kubik").run()
    _tombol(at, "Hitung akar").click().run()
    at.slider(key="nomor_iterasi").set_value(8).run()
    assert not at.exception
    assert "Iterasi 8" in _semua_markdown(at)
    assert "Iterasi berhenti di sini" in _semua_markdown(at)
    assert at.metric


def test_isian_kosong_memberi_peringatan(at):
    _tombol(at, "Hitung akar").click().run()
    assert "Lengkapi semua isian" in at.warning[0].value
    assert not at.metric


def test_interval_tanpa_akar_memberi_error(at):
    _isi(at, "x^2 + 1", -1, 1)
    _tombol(at, "Hitung akar").click().run()
    assert "berbeda tanda" in at.error[0].value


def test_fungsi_tidak_valid_memberi_error_dan_pratinjau_peringatan(at):
    _isi(at, "x^3 + y", 1, 2)
    assert any("tidak dikenali" in c.value for c in at.caption)
    _tombol(at, "Hitung akar").click().run()
    assert "tidak dikenali" in at.error[0].value


def test_belum_konvergen_memberi_peringatan(at):
    _isi(at, "x^10 - 1", 0, 1.3, max_iter=3)
    _tombol(at, "Hitung akar").click().run()
    assert any("Iterasi maksimum tercapai" in w.value for w in at.warning)


def test_cari_interval_mengisi_batas(at):
    at.text_input(key="f_teks").set_value("(x + 3)(x - 1)(x - 4.5)").run()
    _tombol(at, "Cari interval").click().run()
    assert at.number_input(key="a").value == -3
    assert at.number_input(key="b").value == pytest.approx(-2.95)
    assert "Ditemukan 3 selang" in at.info[0].value


def test_cari_interval_tanpa_akar(at):
    at.text_input(key="f_teks").set_value("x^2 + 1").run()
    _tombol(at, "Cari interval").click().run()
    assert "Tidak ada perubahan tanda" in at.warning[0].value


def test_pratinjau_rumus_muncul(at):
    at.text_input(key="f_teks").set_value("e^x = 3").run()
    assert "$f(x) = e^{x} - 3$" in _semua_markdown(at)
