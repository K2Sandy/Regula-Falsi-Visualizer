"""Contoh soal siap pakai yang bisa dipilih di aplikasi.

Semua contoh di sini dicek oleh tests/test_contoh.py: interval mengurung
akar dan metode Regula Falsi konvergen dengan pengaturan yang tertulis.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ContohSoal:
    nama: str        # nama yang tampil di pilihan contoh
    fungsi: str      # teks f(x) persis seperti diketik pengguna
    a: float         # batas bawah interval
    b: float         # batas atas interval
    tol: float       # toleransi error
    max_iter: int    # iterasi maksimum
    akar: float      # akar sebenarnya (untuk dicek di tes)
    catatan: str     # penjelasan singkat yang tampil di aplikasi


DAFTAR_CONTOH: tuple[ContohSoal, ...] = (
    ContohSoal(
        nama="Polinomial kubik",
        fungsi="x^3 - x - 2",
        a=1, b=2, tol=0.0001, max_iter=100,
        akar=1.5213797068,
        catatan="Ujung b tetap di 2 selama semua iterasi, ciri khas Regula Falsi.",
    ),
    ContohSoal(
        nama="Cosinus sama dengan x",
        fungsi="cos(x) - x",
        a=0, b=1, tol=0.0001, max_iter=100,
        akar=0.7390851332,
        catatan="Mencari x yang memenuhi cos(x) = x. Konvergen cepat.",
    ),
    ContohSoal(
        nama="Eksponensial",
        fungsi="e^x - 3",
        a=0, b=2, tol=0.0001, max_iter=100,
        akar=1.0986122887,
        catatan="Akarnya ln(3). Bisa juga ditulis e^x = 3.",
    ),
    ContohSoal(
        nama="Akar kuadrat dari 2",
        fungsi="x^2 - 2",
        a=1, b=2, tol=0.0001, max_iter=100,
        akar=1.4142135624,
        catatan="Menghitung nilai √2 tanpa kalkulator.",
    ),
    ContohSoal(
        nama="Logaritma natural",
        fungsi="ln(x) - 1",
        a=2, b=3, tol=0.0001, max_iter=100,
        akar=2.7182818285,
        catatan="Akarnya bilangan Euler e.",
    ),
    ContohSoal(
        nama="Kasus lambat: x^10 - 1",
        fungsi="x^10 - 1",
        a=0, b=1.3, tol=0.0001, max_iter=100,
        akar=1.0,
        catatan=(
            "Kelemahan Regula Falsi: ujung b macet di 1.3 sehingga butuh "
            "puluhan iterasi, padahal akarnya 1."
        ),
    ),
)


def cari_contoh(nama: str) -> ContohSoal:
    """Ambil contoh berdasarkan namanya. Raise KeyError kalau tidak ada."""
    for contoh in DAFTAR_CONTOH:
        if contoh.nama == nama:
            return contoh
    raise KeyError(f"Contoh '{nama}' tidak ada.")
