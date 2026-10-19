"""Mencari selang [a, b] yang mengurung akar f(x) = 0.

Rentang pencarian dibagi menjadi banyak potongan kecil, lalu dicari potongan
yang ujung-ujungnya berbeda tanda. Perubahan tanda karena kutub (misal 1/x di
x = 0) bukan akar, jadi tiap kandidat dicek dulu dengan beberapa langkah bagi
dua: di sekitar akar |f| mengecil, di sekitar kutub |f| justru membesar.
"""

from collections.abc import Callable

import numpy as np

LANGKAH_CEK = 40


def _nilai(f: Callable[[float], float], x: float) -> float | None:
    """f(x), atau None kalau f tidak terdefinisi di x."""
    try:
        return f(x)
    except (ValueError, ZeroDivisionError, OverflowError):
        return None


def _benar_akar(f: Callable[[float], float], a: float, b: float, fa: float, fb: float) -> bool:
    """True kalau perubahan tanda di [a, b] berasal dari akar, bukan kutub."""
    batas = min(abs(fa), abs(fb))
    for _ in range(LANGKAH_CEK):
        m = (a + b) / 2
        fm = _nilai(f, m)
        if fm is None:
            return False
        if fm == 0:
            return True
        if fa * fm < 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return min(abs(fa), abs(fb)) <= batas


def cari_interval(
    f: Callable[[float], float],
    awal: float = -10.0,
    akhir: float = 10.0,
    potongan: int = 400,
    maksimum: int = 10,
) -> list[tuple[float, float]]:
    """Kembalikan daftar selang (a, b) yang mengurung akar, urut dari kiri.

    f        : fungsi Python f(x)
    awal     : ujung kiri rentang pencarian
    akhir    : ujung kanan rentang pencarian
    potongan : banyak potongan kecil (makin banyak makin teliti, makin lambat)
    maksimum : batas jumlah selang yang dikembalikan

    Raise ValueError kalau rentang atau jumlah potongan tidak valid.
    """
    if not (np.isfinite(awal) and np.isfinite(akhir)) or not awal < akhir:
        raise ValueError("Rentang pencarian tidak valid: awal harus lebih kecil dari akhir.")
    if potongan < 1:
        raise ValueError("Jumlah potongan minimal 1.")

    xs = [round(float(x), 10) for x in np.linspace(awal, akhir, potongan + 1)]
    ys = [_nilai(f, x) for x in xs]

    hasil: list[tuple[float, float]] = []
    for i in range(potongan):
        a, b, fa, fb = xs[i], xs[i + 1], ys[i], ys[i + 1]
        if fa is None or fb is None:
            continue
        if fa == 0 or (fa * fb < 0 and _benar_akar(f, a, b, fa, fb)):
            hasil.append((a, b))
            if len(hasil) >= maksimum:
                break
    # akar tepat di ujung kanan rentang
    if len(hasil) < maksimum and ys[-1] == 0:
        hasil.append((xs[-2], xs[-1]))
    return hasil
