#mengubah teks menjadi parsing python

"""Mengubah teks f(x) dari pengguna menjadi fungsi Python yang bisa dihitung."""

import math

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

X = sp.Symbol("x")

# '^' jadi pangkat, '2x' jadi '2*x'
TRANSFORMASI = standard_transformations + (
    convert_xor,
    implicit_multiplication_application,
)

# e jadi bilangan euler, pi jadi 3.14159...
LOKAL = {"x": X, "e": sp.E, "pi": sp.pi}

def _baca(potongan, teks_asli):
    try:
        return parse_expr(potongan, local_dict=LOKAL, transformations=TRANSFORMASI)
    except Exception:
        raise ValueError(
            f"Fungsi '{teks_asli}' tidak bisa dibaca. Contoh yang valid: x^3 - x - 2, "
            f"cos(x) - x, exp(x) - 3*x, e^x - 3, x^3 - x - 1 = 0"
        )

def parse_fungsi(teks):
    """Ubah string seperti "x^3 - x - 2" menjadi fungsi Python f(x).

    Raise ValueError dengan pesan yang jelas kalau teks tidak valid.
    """
    teks = (teks or "").strip()
    if not teks:
        raise ValueError("Fungsi f(x) belum diisi.")
    if "__" in teks:
        raise ValueError("Teks fungsi mengandung karakter yang tidak diizinkan.")

        if "=" in teks:
            bagian = teks.split("=")
        if len(bagian) != 2 or not bagian[0].strip() or not bagian[1].strip():
            raise ValueError(
                "Format persamaan tidak valid. Pakai satu tanda '=', "
                "contoh: x^3 - x - 1 = 0"
            )
        # pindahkan sisi kanan ke kiri: kiri - kanan = 0
        ekspresi = _baca(bagian[0], teks) - _baca(bagian[1], teks)
    else:
        ekspresi = _baca(teks, teks)

    # hanya boleh ada variabel x
    if not isinstance(ekspresi, sp.Basic) or not ekspresi.free_symbols <= {X}:
        raise ValueError("Fungsi hanya boleh memakai variabel x.")

    fungsi_numpy = sp.lambdify(X, ekspresi, modules="numpy")

    def f(nilai):
        try:
            with np.errstate(all="ignore"):   # bungkam warning numpy (log negatif, dll)
                hasil = float(fungsi_numpy(nilai))
        except Exception:
            raise ValueError(f"f(x) tidak bisa dihitung di x = {nilai:g}.")
        if not math.isfinite(hasil):
            raise ValueError(f"f(x) tidak terdefinisi di x = {nilai:g}.")
        return hasil

    return f
