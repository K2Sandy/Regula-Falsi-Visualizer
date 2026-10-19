"""Mengubah teks f(x) dari pengguna menjadi fungsi Python yang bisa dihitung.

Teks dari pengguna tidak pernah dijalankan mentah-mentah. Sebelum dibaca oleh
sympy, teks diperiksa dulu: hanya karakter matematika dan nama yang ada di
daftar putih yang boleh lewat. Kalau tidak, teks seperti ``exec(...)`` bisa
ikut dieksekusi oleh ``parse_expr`` (yang memakai ``eval`` di balik layar).
"""

import math
import re
import tokenize
from collections.abc import Callable

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)
from sympy.printing.latex import LatexPrinter
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

# simbol hasil salin-tempel dari dokumen/kalkulator yang diubah ke bentuk biasa
_SIMBOL = str.maketrans({
    "\u2212": "-",    # − tanda minus
    "\u2013": "-",    # – en dash
    "\u00d7": "*",    # × kali
    "\u00b7": "*",    # · titik kali
    "\u00f7": "/",    # ÷ bagi
    "\u03c0": "pi",   # π
    "\u00b2": "^2",   # ²
    "\u00b3": "^3",   # ³
    "\u221a": "sqrt", # √
})

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


def _daftar_nama() -> str:
    return ", ".join(sorted(FUNGSI))


def _nama_konstanta_valid(nama: str) -> bool:
    """True kalau nama hanya tersusun dari x, e, dan pi (misal 'xe' = x*e)."""
    bisa = [True] + [False] * len(nama)
    for i in range(len(nama)):
        if not bisa[i]:
            continue
        for potongan in KONSTANTA:
            if nama.startswith(potongan, i):
                bisa[i + len(potongan)] = True
    return bisa[len(nama)]


def _normalkan(teks: str) -> str:
    """Ganti simbol unicode umum (−, ×, ÷, ², ³, π, √) dengan padanan biasa.

    ``√`` ditulis ``√(x)`` atau ``√x``; yang kedua dibaca sebagai ``sqrt x``,
    jadi dibungkus kurung supaya tetap valid.
    """
    teks = re.sub(r"\u221a\s*([A-Za-z0-9.]+)", r"sqrt(\1)", teks)
    return teks.translate(_SIMBOL)


def _periksa_teks(teks: str) -> None:
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


def _baca(potongan: str, teks_asli: str) -> sp.Basic:
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


def parse_ekspresi(teks: str | None) -> sp.Expr:
    """Ubah string seperti "x^3 - x - 2" menjadi ekspresi sympy dalam x.

    Persamaan seperti "e^x = 3" diubah menjadi "e^x - 3". Raise ValueError
    dengan pesan yang jelas kalau teks tidak valid.
    """
    teks = _normalkan((teks or "").strip())
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
        kiri, kanan = _baca(bagian[0], teks), _baca(bagian[1], teks)
        if kanan.is_zero:
            ekspresi = kiri
        else:
            # pindahkan sisi kanan ke kiri: kiri - kanan = 0
            with sp.evaluate(False):
                ekspresi = kiri - kanan
    else:
        ekspresi = _baca(teks, teks)

    # hanya boleh ada variabel x
    if not isinstance(ekspresi, sp.Basic) or not ekspresi.free_symbols <= {X}:
        raise ValueError("Fungsi hanya boleh memakai variabel x.")
    return ekspresi


class _PencetakLatex(LatexPrinter):
    """Pencetak LaTeX yang menulis 3.0 sebagai 3 tanpa mengubah struktur rumus."""

    def _print_Float(self, expr):
        nilai = float(expr)
        if nilai.is_integer() and abs(nilai) < 1e15:
            return str(int(nilai))
        return super()._print_Float(expr)


def ke_latex(teks: str | None) -> str:
    """Ubah teks f(x) menjadi kode LaTeX untuk pratinjau rumus di aplikasi.

    Urutan suku dipertahankan seperti yang diketik (x^3 - x - 2 tetap
    x^3 - x - 2). Raise ValueError kalau teks tidak valid.
    """
    ekspresi = parse_ekspresi(teks)
    try:
        return _PencetakLatex({"order": "none", "ln_notation": True, "min": -6, "max": 15}).doprint(ekspresi)
    except Exception:
        raise ValueError("Rumus f(x) tidak bisa ditampilkan.") from None


def parse_fungsi(teks: str | None) -> Callable[[float], float]:
    """Ubah string seperti "x^3 - x - 2" menjadi fungsi Python f(x).

    Raise ValueError dengan pesan yang jelas kalau teks tidak valid.
    """
    ekspresi = parse_ekspresi(teks)

    fungsi_numpy = sp.lambdify(X, ekspresi, modules="numpy", printer=_PencetakNumpy, docstring_limit=0)

    def f(nilai: float) -> float:
        try:
            with np.errstate(all="ignore"):   # bungkam warning numpy (log negatif, dll)
                hasil = float(fungsi_numpy(nilai))
        except Exception:
            raise ValueError(f"f(x) tidak bisa dihitung di x = {nilai:g}.") from None
        if not math.isfinite(hasil):
            raise ValueError(f"f(x) tidak terdefinisi di x = {nilai:g}.")
        return hasil

    return f
