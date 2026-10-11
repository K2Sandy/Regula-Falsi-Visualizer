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


def parse_fungsi(teks):
    """Ubah string seperti "x^3 - x - 2" menjadi fungsi Python f(x).

    Raise ValueError dengan pesan yang jelas kalau teks tidak valid.
    """
    teks = (teks or "").strip()
    if not teks:
        raise ValueError("Fungsi f(x) belum diisi.")
    if "__" in teks:
        raise ValueError("Teks fungsi mengandung karakter yang tidak diizinkan.")

    try:
        ekspresi = parse_expr(teks, local_dict={"x": X}, transformations=TRANSFORMASI)
    except Exception:
        raise ValueError(
            f"Fungsi '{teks}' tidak bisa dibaca. Contoh yang valid: x^3 - x - 2, "
            f"cos(x) - x, exp(x) - 3*x"
        )

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
