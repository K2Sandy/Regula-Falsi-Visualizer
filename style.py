"""Gaya tampilan aplikasi: kertas grid, tinta navy, stabilo kuning.

Warna dasar dan font diatur di .streamlit/config.toml. File ini hanya
menambah ciri khas yang tidak bisa diatur lewat tema: latar kertas grid,
judul berstabilo, kartu bertepi tinta dengan bayangan tegas, dan tab.
"""

import streamlit as st

CSS = """
:root {
  --kertas: #f1f6f4;
  --tinta: #14213d;
  --pulpen: #2750e6;
  --stabilo: #ffd23f;
  --koreksi: #d7263d;
  --pensil: #56627e;
  --bayangan: 5px 5px 0 var(--tinta);
}

/* kertas grid: garis besar tiap 28px, garis halus tiap 7px */
.stApp {
  background-color: var(--kertas);
  background-image:
    linear-gradient(rgba(20,33,61,.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(20,33,61,.08) 1px, transparent 1px),
    linear-gradient(rgba(20,33,61,.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(20,33,61,.03) 1px, transparent 1px);
  background-size: 28px 28px, 28px 28px, 7px 7px, 7px 7px;
}
.block-container { max-width: 1180px; padding-top: 2.5rem; }

h1, h2, h3 { letter-spacing: -0.03em; }

/* ---------- judul ---------- */
.judul {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-size: clamp(2.6rem, 6vw, 4.2rem);
  font-weight: 800;
  line-height: .95;
  letter-spacing: -0.045em;
  color: var(--tinta);
  margin: 0 0 .9rem;
}
.judul .stabilo {
  background: linear-gradient(
    transparent 56%, var(--stabilo) 56%, var(--stabilo) 90%, transparent 90%
  );
  padding: 0 .08em;
}
.subjudul {
  max-width: 34rem;
  font-size: 1.06rem;
  line-height: 1.55;
  color: var(--pensil);
  margin: 0;
}

/* ---------- kartu ---------- */
.st-key-kartu_rumus,
.st-key-kartu_input,
.st-key-kartu_kosong {
  background: #fff;
  border: 2px solid var(--tinta) !important;
  border-radius: 14px !important;
  box-shadow: var(--bayangan);
}
.st-key-kartu_input { padding: 1.2rem 1.3rem 1.3rem; }
.st-key-kartu_rumus { padding: 1rem 1.2rem .4rem; transform: rotate(-1.2deg); }
.st-key-kartu_kosong { padding: 1.4rem 1.5rem; }
.st-key-kartu_rumus p { color: var(--pensil); margin-bottom: 0; }
.st-key-kartu_kosong { border-style: dashed !important; box-shadow: none; }

/* ---------- tombol ---------- */
.stButton > button,
.stDownloadButton > button {
  font-weight: 700;
  border: 2px solid var(--tinta);
  box-shadow: 4px 4px 0 var(--tinta);
  padding: .55rem 1.6rem;
  transition: transform .12s, box-shadow .12s;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
  border-color: var(--tinta);
  transform: translate(-1px, -1px);
  box-shadow: 5px 5px 0 var(--tinta);
}
.stButton > button:active,
.stDownloadButton > button:active {
  transform: translate(3px, 3px);
  box-shadow: 1px 1px 0 var(--tinta);
}
.stButton > button:focus-visible,
.stDownloadButton > button:focus-visible {
  outline: 3px solid var(--stabilo);
  outline-offset: 3px;
}

/* ---------- angka hasil ---------- */
[data-testid="stMetric"] {
  background: #fff;
  border: 2px solid var(--tinta);
  border-radius: 12px;
  padding: .8rem 1rem;
  box-shadow: 4px 4px 0 var(--tinta);
}
[data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; }
[data-testid="stMetricLabel"] p { color: var(--pensil); font-weight: 600; }

/* ---------- tab ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 1.4rem; border-bottom: 2px solid var(--tinta); }
.stTabs [data-baseweb="tab"] { padding: .5rem 0; font-weight: 600; }
.stTabs [data-baseweb="tab"] p { font-size: 1rem; }
.stTabs [data-baseweb="tab-highlight"] { background: var(--stabilo); height: 6px; border-radius: 0; }
.stTabs [data-baseweb="tab-border"] { display: none; }

/* ---------- tabel ---------- */
[data-testid="stDataFrame"] {
  border: 2px solid var(--tinta);
  border-radius: 12px;
  overflow: hidden;
  font-variant-numeric: tabular-nums;
}

/* ---------- grafik ---------- */
[data-testid="stImage"] img,
[data-testid="stPyplot"] img {
  border: 2px solid var(--tinta);
  border-radius: 12px;
}

.footer {
  margin-top: 3.5rem;
  padding-top: 1.2rem;
  border-top: 2px solid var(--tinta);
  color: var(--pensil);
  font-size: .9rem;
  line-height: 1.6;
}
.footer strong { color: var(--tinta); }

/* ---------- layar kecil ---------- */
@media (max-width: 640px) {
  .block-container { padding-top: 1.5rem; }
  .st-key-kartu_rumus { transform: none; }
  :root { --bayangan: 3px 3px 0 var(--tinta); }
  [data-testid="stMetric"] { box-shadow: 3px 3px 0 var(--tinta); }
  .stTabs [data-baseweb="tab-list"] { gap: .9rem; overflow-x: auto; }
}

@media (prefers-reduced-motion: reduce) {
  .stButton > button, .stDownloadButton > button { transition: none; }
}
"""


def terapkan_gaya() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def judul() -> None:
    kiri, kanan = st.columns([3, 2], gap="large", vertical_alignment="center")
    with kiri:
        st.markdown(
            '<h1 class="judul">Regula <span class="stabilo">Falsi</span></h1>'
            '<p class="subjudul">Cari akar persamaan f(x) = 0 dengan metode posisi palsu. '
            "Ketik fungsinya, tentukan selang, lalu ikuti tiap iterasi di grafik.</p>",
            unsafe_allow_html=True,
        )
    with kanan, st.container(key="kartu_rumus"):
        st.markdown("Titik baru tiap iterasi")
        st.latex(r"c = \frac{a\,f(b) - b\,f(a)}{f(b) - f(a)}")


def footer() -> None:
    st.markdown(
        '<div class="footer">'
        "<strong>Kelompok 3</strong> · Praktikum Komputasi Numerik C<br>"
        "Siti Salwa Shafina · Al Aul Tsaqif · Nawal Azqia · "
        "Syella Zikra Arifa · Keisya Zahira · Muhammad Albharaka Putrosandy"
        "</div>",
        unsafe_allow_html=True,
    )
