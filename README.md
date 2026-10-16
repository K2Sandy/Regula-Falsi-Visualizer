# Regula Falsi Visualizer

Kalkulator persamaan nonlinier berbasis web yang mencari akar `f(x) = 0` dengan
**Metode Regula Falsi** (False Position), lengkap dengan tabel tiap iterasi dan
grafik fungsi. Dibuat dengan Python dan Streamlit untuk Praktikum Komputasi
Numerik.

## Fitur

- Input fungsi dalam bentuk teks biasa, misalnya `x^3 - x - 2`, `cos(x) - x`,
  atau `e^x - 3 = 0`.
- Batas interval, toleransi error, dan iterasi maksimum bisa diatur.
- Validasi input: interval harus valid dan `f(a)` serta `f(b)` harus berbeda
  tanda (akar harus terkurung).
- Tabel iterasi lengkap (`a`, `b`, `c`, `f(a)`, `f(b)`, `f(c)`, error).
- Grafik `f(x)` dengan interval dan akar yang ditandai.

## Cara menjalankan

```bash
git clone https://github.com/K2Sandy/Regula-Falsi-Visualizer.git
cd Regula-Falsi-Visualizer

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

streamlit run app.py
```

Aplikasi terbuka di `http://localhost:8501`.

## Contoh penggunaan

| Fungsi          | a | b | Toleransi | Akar   | Iterasi |
|-----------------|---|---|-----------|--------|---------|
| `x^3 - x - 2`   | 1 | 2 | 0.0001    | 1.5213 | 8       |
| `cos(x) - x`    | 0 | 1 | 0.0001    | 0.7391 | 5       |
| `e^x - 3`       | 0 | 2 | 0.0001    | 1.0986 | 11      |

## Rumus

Titik baru pada tiap iterasi adalah perpotongan garis lurus antara
`(a, f(a))` dan `(b, f(b))` dengan sumbu x:

```
c = (a * f(b) - b * f(a)) / (f(b) - f(a))
```

Setelah itu interval diperbarui: kalau `f(a) * f(c) < 0` maka `b = c`, kalau
tidak maka `a = c`. Iterasi berhenti ketika `f(c) = 0`, error relatif
`|c_baru - c_lama| / |c_baru|` lebih kecil dari toleransi, atau iterasi
maksimum tercapai.

## Struktur proyek

```
app.py            antarmuka Streamlit
regula_falsi.py   inti algoritma Regula Falsi
parsing.py        mengubah teks f(x) menjadi fungsi Python
grafik.py         membuat grafik matplotlib
requirements.txt  daftar dependensi
```

## Lisensi

Belum ditentukan.
