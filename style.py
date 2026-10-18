import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@700;800&family=Figtree:wght@400;500;600;700&display=swap');

html, body, .stApp { font-family: 'Figtree', sans-serif; }

.stApp {
  background-color: #f1f6f4;
  background-image:
    linear-gradient(rgba(20,33,61,.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(20,33,61,.07) 1px, transparent 1px);
  background-size: 28px 28px;
}

h1, h2, h3 {
  font-family: 'Bricolage Grotesque', sans-serif !important;
  letter-spacing: -0.03em;
  color: #14213d;
}
.judul { font-family: 'Bricolage Grotesque', sans-serif; font-size: 3.4rem; font-weight: 800; line-height: 1; color: #14213d; }
.judul .stabilo {
  background: linear-gradient(transparent 58%, #ffd23f 58%, #ffd23f 92%, transparent 92%);
  padding: 0 .1em;
}

[data-testid="stTextInputRootElement"], [data-testid="stNumberInputContainer"] {
  border: 2px solid #14213d !important;
  border-radius: 10px !important;
  background: #ffffff !important;
}

.stButton > button {
  background: #2750e6; color: #fff; font-weight: 700;
  border: 2px solid #14213d; border-radius: 12px;
  box-shadow: 4px 4px 0 #14213d; padding: .6rem 2rem;
  transition: transform .12s, box-shadow .12s;
}
.stButton > button:hover {
  color: #fff; border-color: #14213d;
  transform: translate(-1px, -1px); box-shadow: 5px 5px 0 #14213d;
}

[data-testid="stMetric"] {
  background: #fff; border: 2px solid #14213d; border-radius: 12px;
  padding: .8rem 1rem; box-shadow: 4px 4px 0 #14213d;
}

[data-testid="stDataFrame"] {
  border: 2px solid #14213d; border-radius: 12px; overflow: hidden;
}

.footer { margin-top: 3rem; color: #56627e; font-size: .85rem; text-align: center; }
</style>
"""

def terapkan_gaya():
    st.markdown(CSS, unsafe_allow_html=True)

def judul():
    st.markdown('<div class="judul">Regula <span class="stabilo">Falsi</span></div>',
                unsafe_allow_html=True)
    st.caption("Cari akar persamaan dengan metode posisi palsu. Masukkan fungsi dan selang, lalu ikuti hitungan tiap iterasi.")
    st.latex(r"c = b - \frac{f(b)\,(b-a)}{f(b)-f(a)}")

def footer():
    st.markdown(
        '<div class="footer">'
        '<strong>Kelompok 3</strong> · Praktikum Komputasi Numerik C<br>'
        'Siti Salwa Shafina · Al Aul Tsaqif · Nawal Azqia · '
        'Syella Zikra Arifa · Keisya Zahira · Muhammad Albharaka Putrosandy'
        '</div>',
        unsafe_allow_html=True,
    )