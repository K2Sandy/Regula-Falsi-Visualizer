# Cara kerja Metode Regula Falsi

Dokumen ini menjelaskan algoritma yang dipakai di `regula_falsi.py` dan contoh
perhitungannya, supaya hasil di tabel iterasi mudah dicek dengan tangan.

## Ide dasar

Misalkan `f` kontinu di `[a, b]` dan `f(a) * f(b) < 0`. Artinya grafik `f`
memotong sumbu x setidaknya sekali di dalam interval (akar terkurung).

Regula Falsi menarik garis lurus dari titik `(a, f(a))` ke `(b, f(b))`, lalu
memakai titik potong garis itu dengan sumbu x sebagai tebakan akar:

```
c = (a * f(b) - b * f(a)) / (f(b) - f(a))
```

Bedanya dengan metode bagi dua (bisection): titik `c` tidak selalu di tengah
interval, tetapi lebih dekat ke ujung yang nilai `|f|`-nya lebih kecil.

## Langkah per iterasi

1. Hitung `c` dengan rumus di atas, lalu `f(c)`.
2. Hitung error relatif terhadap `c` iterasi sebelumnya:
   `|c_baru - c_lama| / |c_baru|`.
3. Cek kriteria berhenti (lihat bagian bawah).
4. Perbarui interval:
   - kalau `f(a) * f(c) < 0`, akar ada di `[a, c]` jadi `b = c`
   - kalau tidak, akar ada di `[c, b]` jadi `a = c`

## Kriteria berhenti

| Kondisi                          | Hasil                                         |
|----------------------------------|-----------------------------------------------|
| `f(c) = 0`                       | akar tepat ditemukan                          |
| error < toleransi                | konvergen                                     |
| iterasi mencapai batas maksimum  | berhenti, ditandai belum konvergen            |

Kasus khusus:

- Kalau `f(a)` atau `f(b)` sudah 0, ujung itu langsung menjadi akar (0 iterasi).
- Kalau `|c| <= toleransi` (akar sangat dekat 0), error relatif bisa bagi nol
  dan tidak pernah mengecil, jadi dipakai error absolut `|c_baru - c_lama|`.
- Iterasi pertama belum punya pembanding, jadi errornya kosong (`-`).

## Contoh: f(x) = x^3 - x - 2 pada [1, 2], toleransi 0.0001

`f(1) = -2` dan `f(2) = 4` berbeda tanda, jadi akar terkurung.

| Iter | a        | b        | c        | f(a)      | f(b)     | f(c)      | Error    |
|------|----------|----------|----------|-----------|----------|-----------|----------|
| 1    | 1.000000 | 2.000000 | 1.333333 | -2.000000 | 4.000000 | -0.962963 | -        |
| 2    | 1.333333 | 2.000000 | 1.462687 | -0.962963 | 4.000000 | -0.333339 | 8.84e-02 |
| 3    | 1.462687 | 2.000000 | 1.504019 | -0.333339 | 4.000000 | -0.101818 | 2.75e-02 |
| 4    | 1.504019 | 2.000000 | 1.516331 | -0.101818 | 4.000000 | -0.029895 | 8.12e-03 |
| 5    | 1.516331 | 2.000000 | 1.519919 | -0.029895 | 4.000000 | -0.008675 | 2.36e-03 |
| 6    | 1.519919 | 2.000000 | 1.520957 | -0.008675 | 4.000000 | -0.002509 | 6.83e-04 |
| 7    | 1.520957 | 2.000000 | 1.521258 | -0.002509 | 4.000000 | -0.000725 | 1.97e-04 |
| 8    | 1.521258 | 2.000000 | 1.521344 | -0.000725 | 4.000000 | -0.000209 | 5.70e-05 |

Iterasi 8 berhenti karena error `5.70e-05 < 0.0001`. Akar hampirannya
`1.521344` (akar sebenarnya `1.521380`).

Perhatikan kolom `b`: nilainya tetap 2 di semua iterasi. Itu ciri khas Regula
Falsi, satu ujung interval bisa "macet" sementara ujung lainnya mendekati akar.
Karena itu pada beberapa fungsi konvergensinya lebih lambat dari yang
dibayangkan, dan kriteria berhenti memakai selisih `c`, bukan lebar interval.

## Format input fungsi

Teks fungsi dibaca oleh `parsing.py` dan hanya menerima yang ada di daftar putih.

- Variabel hanya `x`. Konstanta: `e` (bilangan Euler) dan `pi`.
- Operator: `+ - * / ^` (atau `**`), kurung, dan perkalian tanpa tanda (`2x`).
- Fungsi: `sin cos tan cot sec csc asin acos atan sinh cosh tanh asinh acosh
  atanh exp log ln log10 log2 sqrt cbrt abs`. `log` dan `ln` adalah logaritma
  natural.
- Boleh ditulis sebagai persamaan: `e^x = 3` dibaca `e^x - 3 = 0`.
- Simbol hasil salin-tempel seperti `−`, `×`, `÷`, `²`, `³`, `π`, dan `√`
  otomatis diubah ke bentuk biasa.
- Maksimal 200 karakter. Teks di luar aturan ini ditolak dengan pesan error.
