"""Inti algoritma Metode Regula Falsi (False Position).

Rumus titik baru:
    c = (a * f(b) - b * f(a)) / (f(b) - f(a))
"""

import math
from dataclasses import dataclass, field


@dataclass
class HasilRegulaFalsi:
    akar: float                 # nilai akar hasil akhir
    iterasi: int                # jumlah iterasi yang dilakukan
    error: float                # error relatif terakhir (None kalau cuma 1 iterasi)
    konvergen: bool             # True kalau berhenti karena memenuhi toleransi
    alasan: str                 # penjelasan kenapa iterasi berhenti
    tabel: list = field(default_factory=list)  # satu dict per iterasi


def _hitung_error(c, c_lama, tol):
    """Hitung error perkiraan akar antara dua iterasi berurutan.

    Biasanya error relatif |c - c_lama| / |c|. Kalau akar sangat dekat 0
    (|c| <= tol), error relatif tidak pernah mengecil dan bisa bagi nol, jadi
    dipakai error absolut |c - c_lama|. Mengembalikan None di iterasi pertama
    karena belum ada nilai pembanding.
    """
    if c_lama is None:
        return None
    if abs(c) > tol:
        return abs((c - c_lama) / c)
    return abs(c - c_lama)


def regula_falsi(f, a, b, tol=1e-6, max_iter=100):
    """Cari akar f(x) = 0 di interval [a, b] dengan metode Regula Falsi.

    f        : fungsi Python yang menerima angka dan mengembalikan angka
    a, b     : batas interval, syarat a < b dan f(a) * f(b) < 0
    tol      : toleransi error (kriteria berhenti)
    max_iter : jumlah iterasi maksimum (kriteria berhenti)

    Raise ValueError kalau input tidak valid.
    """
    # --- validasi input ---
    if not all(math.isfinite(nilai) for nilai in (a, b, tol)):
        raise ValueError(
            "Batas interval dan toleransi harus berupa bilangan biasa "
            "(bukan NaN atau tak hingga)."
        )
    if not a < b:
        raise ValueError("Batas bawah (a) harus lebih kecil dari batas atas (b).")
    if tol <= 0:
        raise ValueError("Toleransi error harus lebih besar dari 0.")
    if max_iter < 1:
        raise ValueError("Iterasi maksimum minimal 1.")

    fa, fb = f(a), f(b)

    if fa * fb > 0:
        raise ValueError(
            f"f(a) dan f(b) harus berbeda tanda (akar harus terkurung). "
            f"Sekarang f({a:g}) = {fa:.6g} dan f({b:g}) = {fb:.6g}."
        )

    # kasus khusus: salah satu ujung interval sudah akar
    if fa == 0 or fb == 0:
        akar = a if fa == 0 else b
        return HasilRegulaFalsi(
            akar=akar, iterasi=0, error=0.0, konvergen=True,
            alasan="Salah satu ujung interval sudah merupakan akar.",
        )

    tabel = []
    c_lama = None
    error = None

    for i in range(1, max_iter + 1):
        # titik potong garis (a, f(a)) - (b, f(b)) dengan sumbu x
        c = (a * fb - b * fa) / (fb - fa)
        fc = f(c)

        error = _hitung_error(c, c_lama, tol)

        tabel.append({
            "Iterasi": i,
            "a": a, "b": b, "c": c,
            "f(a)": fa, "f(b)": fb, "f(c)": fc,
            "Error": error,
        })

        # --- kriteria berhenti ---
        if fc == 0:
            return HasilRegulaFalsi(c, i, 0.0, True,
                                    "f(c) = 0, akar tepat ditemukan.", tabel)
        if error is not None and error < tol:
            return HasilRegulaFalsi(c, i, error, True,
                                    "Error sudah lebih kecil dari toleransi.", tabel)

        # --- perbarui interval ---
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
        c_lama = c

    return HasilRegulaFalsi(c, max_iter, error, False,
                            "Iterasi maksimum tercapai sebelum error < toleransi.",
                            tabel)
