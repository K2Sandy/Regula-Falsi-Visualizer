#disini algoritmanya

"""Inti algoritma Metode Regula Falsi (False Position).

Rumus titik baru:
    c = (a * f(b) - b * f(a)) / (f(b) - f(a))
"""

from dataclasses import dataclass, field


@dataclass
class HasilRegulaFalsi:
    akar: float                 # nilai akar hasil akhir
    iterasi: int                # jumlah iterasi yang dilakukan
    error: float                # error relatif terakhir (None kalau cuma 1 iterasi)
    konvergen: bool             # True kalau berhenti karena memenuhi toleransi
    alasan: str                 # penjelasan kenapa iterasi berhenti
    tabel: list = field(default_factory=list)  # satu dict per iterasi


def regula_falsi(f, a, b, tol=1e-6, max_iter=100):
    """Cari akar f(x) = 0 di interval [a, b] dengan metode Regula Falsi.

    f        : fungsi Python yang menerima angka dan mengembalikan angka
    a, b     : batas interval
    tol      : toleransi error (kriteria berhenti)
    max_iter : jumlah iterasi maksimum (kriteria berhenti)
    """
    fa, fb = f(a), f(b)
    tabel = []
    c_lama = None
    error = None

    for i in range(1, max_iter + 1):
        # titik potong garis (a, f(a)) - (b, f(b)) dengan sumbu x
        c = (a * fb - b * fa) / (fb - fa)
        fc = f(c)

        # error relatif |c_baru - c_lama| / |c_baru|
        if c_lama is None:
            error = None            # iterasi pertama belum punya pembanding
        elif c != 0:
            error = abs((c - c_lama) / c)
        else:
            error = abs(c - c_lama)  # hindari bagi nol kalau akarnya tepat 0

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
