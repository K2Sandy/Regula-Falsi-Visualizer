"""Mengubah teks f(x) dari pengguna menjadi fungsi Python yang bisa dihitung.

Teks dari pengguna tidak pernah dijalankan mentah-mentah. Sebelum dibaca oleh
sympy, teks diperiksa dulu: hanya karakter matematika dan nama yang ada di
daftar putih yang boleh lewat. Kalau tidak, teks seperti ``exec(...)`` bisa
ikut dieksekusi oleh ``parse_expr`` (yang memakai ``eval`` di balik layar).
"""

import math
import re
import tokenize

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)
from sympy.printing.numpy import NumPyPrinter

X = sp.Symbol("x")

MAKS_PANJANG = 200

# fungsi matematika yang boleh dipakai di teks f(x)
FUNGSI = (
    "sin", "cos", "tan", "cot", "sec", "csc",
    "asin", "acos", "atan",
    "sinh", "cosh", "tanh", "asinh", "acosh", "atanh",
    "exp", "log", "ln", "log10", "log2", "sqrt", "cbrt", "abs",
)

# konstanta dan variabel yang boleh dipakai (e = bilangan Euler)
KONSTANTA = ("x", "e", "pi")

# nama yang dikenali sympy: "e" jadi bilangan Euler, "pi" jadi 3,14159...
LOKAL = {
    "x": X,
    "e": sp.E,
    "pi": sp.pi,
    # log() di sympy adalah logaritma natural, jadi basis 10 dan 2 dibuat sendiri
    "log10": lambda nilai: sp.log(nilai) / sp.log(10),
    "log2": lambda nilai: sp.log(nilai) / sp.log(2),
}

_KARAKTER_BOLEH = re.compile(r"[0-9A-Za-z+\-*/^().,=\s]*")
# angka yang berdiri sendiri (bukan bagian dari nama seperti log10)
_ANGKA = re.compile(r"(?<![A-Za-z0-9.])(?:\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)")
_NAMA = re.compile(r"[A-Za-z][A-Za-z0-9]*")


def _bilangan_bulat_ke_float(tokens, local_dict, global_dict):
    """Ubah literal bulat (2, 10, ...) menjadi float (2.0, 10.0, ...).

    Tanpa ini, teks seperti ``9^9^9^9`` memaksa sympy dan Python menghitung
    bilangan bulat raksasa sampai aplikasi macet. Dengan float, hasil yang
    terlalu besar langsung memicu OverflowError yang bisa ditangkap.
    """
    hasil = []
    for jenis, nilai in tokens:
        if jenis == tokenize.NUMBER and nilai.isdigit():
            nilai = f"{nilai}.0"
        hasil.append((jenis, nilai))
    return hasil


# '^' jadi pangkat, '2x' jadi '2*x'
TRANSFORMASI = (
    (_bilangan_bulat_ke_float,)
    + standard_transformations
    + (convert_xor, implicit_multiplication_application)
)


class _PencetakNumpy(NumPyPrinter):
    """Pencetak kode numpy yang tidak mengurutkan suku penjumlahan.

    Pencetak bawaan mengurutkan suku dengan menghitung nilai numeriknya lewat
    mpmath. Untuk teks seperti ``9^9^9^9 + x`` itu memicu perhitungan bilangan
    raksasa dan aplikasi macet. Urutan suku tidak memengaruhi hasil f(x).
    """

    def _as_ordered_terms(self, expr, order=None):
        return list(expr.args)


def _daftar_nama():
    return ", ".join(sorted(FUNGSI))


def _nama_konstanta_valid(nama):
    """True kalau nama hanya tersusun dari x, e, dan pi (misal 'xe' = x*e)."""
    bisa = [True] + [False] * len(nama)
    for i in range(len(nama)):
        if not bisa[i]:
            continue
        for potongan in KONSTANTA:
            if nama.startswith(potongan, i):
                bisa[i + len(potongan)] = True
    return bisa[len(nama)]


def _periksa_teks(teks):
    """Pastikan teks hanya berisi karakter dan nama yang diizinkan."""
    if len(teks) > MAKS_PANJANG:
        raise ValueError(f"Fungsi terlalu panjang (maksimal {MAKS_PANJANG} karakter).")
    if not _KARAKTER_BOLEH.fullmatch(teks):
        raise ValueError("Teks fungsi mengandung karakter yang tidak diizinkan.")

    tanpa_angka = _ANGKA.sub(" 0 ", teks)
    for nama in _NAMA.findall(tanpa_angka):
        if nama in FUNGSI or _nama_konstanta_valid(nama):
            continue
        raise ValueError(
            f"Nama '{nama}' tidak dikenali. Fungsi hanya boleh memakai variabel x, "
            f"konstanta e dan pi, serta fungsi: {_daftar_nama()}."
        )


def _baca(potongan, teks_asli):
    """Ubah satu potongan teks menjadi ekspresi sympy."""
    try:
        return parse_expr(
            potongan,
            local_dict=dict(LOKAL),
            transformations=TRANSFORMASI,
            evaluate=False,
        )
    except Exception:
        raise ValueError(
            f"Fungsi '{teks_asli}' tidak bisa dibaca. Contoh yang valid: x^3 - x - 2, "
            f"cos(x) - x, exp(x) - 3*x, e^x - 3, x^3 - x - 1 = 0"
        ) from None


def parse_fungsi(teks):
    """Ubah string seperti "x^3 - x - 2" menjadi fungsi Python f(x).

    Raise ValueError dengan pesan yang jelas kalau teks tidak valid.
    """
    teks = (teks or "").strip()
    if not teks:
        raise ValueError("Fungsi f(x) belum diisi.")
    _periksa_teks(teks)

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

    fungsi_numpy = sp.lambdify(X, ekspresi, modules="numpy", printer=_PencetakNumpy, docstring_limit=0)

    def f(nilai):
        try:
            with np.errstate(all="ignore"):   # bungkam warning numpy (log negatif, dll)
                hasil = float(fungsi_numpy(nilai))
        except Exception:
            raise ValueError(f"f(x) tidak bisa dihitung di x = {nilai:g}.") from None
        if not math.isfinite(hasil):
            raise ValueError(f"f(x) tidak terdefinisi di x = {nilai:g}.")
        return hasil

    return f
