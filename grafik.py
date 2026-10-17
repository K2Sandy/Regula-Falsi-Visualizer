"""Grafik fungsi f(x) beserta interval dan akar."""

from collections.abc import Callable
from typing import TYPE_CHECKING

import numpy as np
from matplotlib.figure import Figure

if TYPE_CHECKING:
    from regula_falsi import HasilRegulaFalsi


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

    ys = []
    for x in xs:
        try:
            ys.append(f(x))
        except ValueError:      # titik di luar domain fungsi (misal log negatif)
            ys.append(np.nan)

    fig = Figure(figsize=(7, 4))
    ax = fig.subplots()

    ax.plot(xs, ys, label="f(x)")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(a, color="gray", linestyle="--", linewidth=0.8, label=f"a = {a:g}")
    ax.axvline(b, color="gray", linestyle="--", linewidth=0.8, label=f"b = {b:g}")

    if hasil is not None:
        ax.plot(hasil.akar, 0, "ro", label=f"akar ≈ {hasil.akar:.6g}")

    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.set_title("Grafik f(x)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig
