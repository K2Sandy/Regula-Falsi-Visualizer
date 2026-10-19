"""Grafik fungsi f(x) beserta interval dan akar.

Warna mengikuti tema aplikasi (lihat style.py): tinta navy, pulpen biru,
stabilo kuning untuk interval, dan merah koreksi untuk akar.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import AutoMinorLocator

if TYPE_CHECKING:
    from regula_falsi import HasilRegulaFalsi

TINTA = "#14213d"     # garis sumbu, teks
PULPEN = "#2750e6"    # kurva f(x)
STABILO = "#ffd23f"   # arsiran interval
KOREKSI = "#d7263d"   # titik akar
PENSIL = "#56627e"    # garis bantu


def _siapkan_sumbu(fig: Figure) -> Axes:
    """Buat satu sumbu bergaya kertas grafik: grid mayor dan minor, tanpa bingkai atas/kanan."""
    fig.patch.set_facecolor("white")
    ax = fig.subplots()
    ax.set_facecolor("white")
    for sisi in ("top", "right"):
        ax.spines[sisi].set_visible(False)
    for sisi in ("left", "bottom"):
        ax.spines[sisi].set_color(TINTA)
        ax.spines[sisi].set_linewidth(1.2)
    ax.tick_params(colors=TINTA, labelsize=9)
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.grid(True, which="major", color=TINTA, alpha=0.14, linewidth=0.8)
    ax.grid(True, which="minor", color=TINTA, alpha=0.05, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.xaxis.label.set_color(TINTA)
    ax.yaxis.label.set_color(TINTA)
    return ax


def _hitung_kurva(f: Callable[[float], float], xs: np.ndarray) -> np.ndarray:
    """Hitung f di tiap x. Titik di luar domain (misal log negatif) menjadi NaN."""
    ys = []
    for x in xs:
        try:
            ys.append(f(x))
        except ValueError:
            ys.append(np.nan)
    return np.asarray(ys, dtype=float)


def _putus_di_kutub(ys: np.ndarray) -> np.ndarray:
    """Ganti titik setelah lompatan tanda yang sangat besar dengan NaN.

    Di kutub (misal x = 1 pada 1/(x - 1)) kurva melompat dari -besar ke
    +besar. Tanpa diputus, matplotlib menggambar garis tegak palsu.
    """
    ys = ys.copy()
    terhingga = ys[np.isfinite(ys)]
    if terhingga.size < 2:
        return ys
    bawah, atas = np.percentile(terhingga, [2, 98])
    batas_lompat = 4 * max(atas - bawah, 1e-12)
    lompat = (np.abs(np.diff(ys)) > batas_lompat) & (np.sign(ys[:-1]) != np.sign(ys[1:]))
    ys[1:][lompat] = np.nan
    return ys


def _batasi_y(ax: Axes, ys: np.ndarray) -> None:
    """Potong sumbu y di sekitar kutub supaya kurva tetap terbaca.

    Tanpa ini, fungsi seperti 1/(x - 1) membuat sumbu y sampai jutaan dan
    bagian penting grafik jadi garis datar.
    """
    terhingga = ys[np.isfinite(ys)]
    if terhingga.size < 2:
        return
    bawah, atas = np.percentile(terhingga, [2, 98])
    rentang_penuh = terhingga.max() - terhingga.min()
    if atas - bawah <= 0 or rentang_penuh <= 4 * (atas - bawah):
        return
    margin = 0.15 * (atas - bawah)
    ax.set_ylim(min(bawah - margin, -margin), max(atas + margin, margin))


def _legenda(ax: Axes) -> None:
    legenda = ax.legend(frameon=True, fontsize=9, loc="best")
    legenda.get_frame().set_edgecolor(TINTA)
    legenda.get_frame().set_linewidth(1)
    for teks in legenda.get_texts():
        teks.set_color(TINTA)


def buat_grafik(
    f: Callable[[float], float],
    a: float,
    b: float,
    hasil: "HasilRegulaFalsi | None" = None,
) -> Figure:
    """Buat grafik f(x) di sekitar [a, b] dan kembalikan objek Figure matplotlib.

    hasil : objek HasilRegulaFalsi (opsional). Kalau ada, akar ikut ditandai.
    """
    lebar = b - a
    xs = np.linspace(a - 0.25 * lebar, b + 0.25 * lebar, 400)
    ys = _hitung_kurva(f, xs)

    fig = Figure(figsize=(7, 4.2))
    ax = _siapkan_sumbu(fig)

    ax.plot(xs, _putus_di_kutub(ys), color=PULPEN, linewidth=2.4, label="f(x)", zorder=3)
    ax.axhline(0, color=TINTA, linewidth=1.1, zorder=2)
    ax.axvspan(a, b, color=STABILO, alpha=0.28, linewidth=0, zorder=1)
    ax.axvline(a, color=PENSIL, linestyle="--", linewidth=1, label=f"a = {a:g}", zorder=2)
    ax.axvline(b, color=PENSIL, linestyle=":", linewidth=1.2, label=f"b = {b:g}", zorder=2)

    if hasil is not None:
        ax.plot(
            hasil.akar, 0, "o", markersize=9, color=KOREKSI,
            markeredgecolor="white", markeredgewidth=1.5,
            label=f"akar ≈ {hasil.akar:.6g}", zorder=5,
        )

    _batasi_y(ax, ys)
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    _legenda(ax)
    fig.tight_layout()
    return fig


def buat_grafik_iterasi(
    f: Callable[[float], float],
    a: float,
    b: float,
    hasil: "HasilRegulaFalsi",
    nomor: int,
) -> Figure:
    """Gambar apa yang terjadi di iterasi ke-`nomor` (mulai dari 1).

    a, b  : interval awal, supaya skala grafik sama di semua iterasi
    hasil : objek HasilRegulaFalsi dengan tabel iterasi

    Yang digambar: kurva f(x), interval iterasi itu (arsiran), garis lurus dari
    (a, f(a)) ke (b, f(b)), titik potong c di sumbu x, nilai f(c), dan titik c
    dari iterasi sebelumnya sebagai jejak. Raise ValueError kalau nomor tidak ada.
    """
    if not 1 <= nomor <= len(hasil.tabel):
        raise ValueError(f"Iterasi {nomor} tidak ada. Pilih 1 sampai {len(hasil.tabel)}.")
    baris = hasil.tabel[nomor - 1]
    ai, bi, c = baris["a"], baris["b"], baris["c"]
    fa, fb, fc = baris["f(a)"], baris["f(b)"], baris["f(c)"]

    lebar = b - a
    xs = np.linspace(a - 0.1 * lebar, b + 0.1 * lebar, 400)
    ys = _hitung_kurva(f, xs)

    fig = Figure(figsize=(7, 4.2))
    ax = _siapkan_sumbu(fig)

    ax.plot(xs, _putus_di_kutub(ys), color=PULPEN, linewidth=2.4, label="f(x)", zorder=3)
    ax.axhline(0, color=TINTA, linewidth=1.1, zorder=2)
    ax.axvspan(ai, bi, color=STABILO, alpha=0.28, linewidth=0, zorder=1,
               label=f"[a, b] = [{ai:.4g}, {bi:.4g}]")

    # garis lurus (a, f(a)) - (b, f(b)) yang memotong sumbu x di c
    ax.plot([ai, bi], [fa, fb], color=TINTA, linewidth=1.4, label="garis potong", zorder=4)
    ax.plot([ai, bi], [fa, fb], "o", color=TINTA, markersize=5, zorder=4)
    ax.plot([c, c], [0, fc], color=KOREKSI, linestyle=":", linewidth=1.4, zorder=4)

    jejak = [baris_lama["c"] for baris_lama in hasil.tabel[: nomor - 1]]
    if jejak:
        ax.plot(jejak, [0] * len(jejak), "o", color=PENSIL, alpha=0.45, markersize=5,
                label="c sebelumnya", zorder=4)

    ax.plot(c, 0, "o", markersize=9, color=KOREKSI, markeredgecolor="white",
            markeredgewidth=1.5, label=f"c = {c:.6g}", zorder=5)

    _batasi_y(ax, ys)
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.set_title(f"Iterasi {nomor} dari {len(hasil.tabel)}", color=TINTA, fontsize=11, loc="left")
    _legenda(ax)
    fig.tight_layout()
    return fig


def buat_grafik_konvergensi(hasil: "HasilRegulaFalsi", tol: float) -> Figure:
    """Grafik error dan |f(c)| tiap iterasi dalam skala logaritmik.

    Garis toleransi ikut digambar, jadi terlihat di iterasi mana error
    menembus toleransi. Nilai 0 (akar tepat) tidak bisa digambar di skala log
    sehingga dilewati.
    """
    iterasi = [baris["Iterasi"] for baris in hasil.tabel]
    error = [baris["Error"] for baris in hasil.tabel]
    fc = [abs(baris["f(c)"]) for baris in hasil.tabel]

    fig = Figure(figsize=(7, 4.2))
    ax = _siapkan_sumbu(fig)

    titik_error = [(i, e) for i, e in zip(iterasi, error, strict=True) if e is not None and e > 0]
    titik_fc = [(i, v) for i, v in zip(iterasi, fc, strict=True) if v > 0]

    if not titik_error and not titik_fc:
        ax.text(0.5, 0.5, "Tidak ada error untuk digambar.\nAkar ditemukan tanpa perlu iterasi lanjutan.",
                ha="center", va="center", color=PENSIL, transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        for sisi in ("left", "bottom"):
            ax.spines[sisi].set_visible(False)
        fig.tight_layout()
        return fig

    if titik_error:
        xs, ys = zip(*titik_error, strict=True)
        ax.plot(xs, ys, "o-", color=PULPEN, linewidth=2.2, markersize=5, label="error relatif", zorder=3)
    if titik_fc:
        xs, ys = zip(*titik_fc, strict=True)
        ax.plot(xs, ys, "s--", color=PENSIL, linewidth=1.2, markersize=4, label="|f(c)|", zorder=3)

    ax.set_yscale("log")
    ax.axhline(tol, color=KOREKSI, linewidth=1.2, linestyle="--", label=f"toleransi = {tol:g}", zorder=2)
    ax.axhspan(ax.get_ylim()[0], tol, color=STABILO, alpha=0.22, linewidth=0, zorder=1)
    ax.set_xlabel("Iterasi")
    ax.set_ylabel("Nilai (skala log)")
    ax.xaxis.get_major_locator().set_params(integer=True)
    _legenda(ax)
    fig.tight_layout()
    return fig
