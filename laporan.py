"""Mengubah hasil Regula Falsi menjadi penjelasan, tabel, dan file CSV."""

import pandas as pd

from regula_falsi import HasilRegulaFalsi

KOLOM = ["Iterasi", "a", "b", "c", "f(a)", "f(b)", "f(c)", "Error"]


def _angka(nilai: float) -> str:
    """Format angka ringkas: 1.333333, -0.962963, 5.7e-05."""
    return f"{nilai:.6g}"


def jelaskan_iterasi(hasil: HasilRegulaFalsi, nomor: int, tol: float) -> list[str]:
    """Jelaskan apa yang terjadi di iterasi ke-`nomor` dalam beberapa kalimat.

    hasil : objek HasilRegulaFalsi
    nomor : nomor iterasi, mulai dari 1
    tol   : toleransi yang dipakai saat menghitung

    Raise ValueError kalau nomor iterasi tidak ada di tabel.
    """
    if not 1 <= nomor <= len(hasil.tabel):
        raise ValueError(f"Iterasi {nomor} tidak ada. Pilih 1 sampai {len(hasil.tabel)}.")

    baris = hasil.tabel[nomor - 1]
    a, b, c = baris["a"], baris["b"], baris["c"]
    fa, fc = baris["f(a)"], baris["f(c)"]
    error = baris["Error"]
    terakhir = nomor == len(hasil.tabel)

    kalimat = [
        f"Tarik garis lurus dari (a, f(a)) = ({_angka(a)}, {_angka(fa)}) "
        f"ke (b, f(b)) = ({_angka(b)}, {_angka(baris['f(b)'])}).",
        f"Garis itu memotong sumbu x di c = {_angka(c)}, dengan f(c) = {_angka(fc)}.",
    ]

    if error is None:
        kalimat.append("Ini iterasi pertama, jadi error belum bisa dihitung.")
    elif error < tol:
        kalimat.append(f"Error = {error:.3e}, sudah lebih kecil dari toleransi {tol:g}.")
    else:
        kalimat.append(f"Error = {error:.3e}, masih lebih besar dari toleransi {tol:g}.")

    if terakhir:
        kalimat.append(f"Iterasi berhenti di sini. {hasil.alasan}")
    elif fc == 0:
        kalimat.append("f(c) = 0, jadi c adalah akar tepat.")
    elif fa * fc < 0:
        kalimat.append(
            "f(a) dan f(c) berbeda tanda, jadi akar ada di [a, c]. "
            f"Untuk iterasi berikutnya b diganti dengan c = {_angka(c)}."
        )
    else:
        kalimat.append(
            "f(a) dan f(c) bertanda sama, jadi akar ada di [c, b]. "
            f"Untuk iterasi berikutnya a diganti dengan c = {_angka(c)}."
        )
    return kalimat


def tabel_ke_dataframe(hasil: HasilRegulaFalsi) -> pd.DataFrame:
    """Ubah tabel iterasi menjadi DataFrame dengan urutan kolom tetap.

    Error iterasi pertama (None) menjadi NaN supaya kolomnya tetap bertipe angka.
    """
    df = pd.DataFrame(hasil.tabel, columns=KOLOM)
    df["Error"] = pd.to_numeric(df["Error"])
    return df


def tabel_ke_csv(hasil: HasilRegulaFalsi) -> bytes:
    """Ubah tabel iterasi menjadi isi file CSV (UTF-8) untuk diunduh.

    Angka ditulis sampai 12 angka penting dan error kosong menjadi sel kosong.
    """
    return tabel_ke_dataframe(hasil).to_csv(index=False, float_format="%.12g").encode("utf-8")
