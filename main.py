import streamlit as st
import pandas as pd
import time
from pathlib import Path
from pipeline import ExtractionPipeline

# ================= KONFIGURASI =================
st.set_page_config(
    page_title="InfoExract · Bengkel Motor",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= CSS =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset ── */
#MainMenu, header, footer { visibility: hidden; }
*, *::before, *::after { box-sizing: border-box; }

/* ── Base ── */
html, body, .stApp {
    background-color: #0E0F14 !important;
    color: #C9CDD6;
    font-family: 'Inter', sans-serif;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #13141A !important;
    border-right: 1px solid #1E2028;
}

/* ── Header strip ── */
.ie-header {
    padding: 48px 0 36px 0;
    border-bottom: 1px solid #1E2028;
    margin-bottom: 40px;
}
.ie-header .eyebrow {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #E07B39;
    margin-bottom: 10px;
}
.ie-header h1 {
    font-size: 28px;
    font-weight: 700;
    color: #E8EAF0;
    margin: 0 0 8px 0;
    line-height: 1.2;
    letter-spacing: -0.02em;
}
.ie-header .subtitle {
    font-size: 14px;
    color: #606673;
    font-weight: 400;
    margin: 0;
}

/* ── Input section ── */
.input-label {
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #606673;
    margin-bottom: 8px;
}

.stTextInput > div > div > input {
    background-color: #13141A !important;
    color: #C9CDD6 !important;
    border: 1px solid #272930 !important;
    border-radius: 6px !important;
    padding: 14px 16px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    transition: border-color 0.15s ease;
}
.stTextInput > div > div > input:focus {
    border-color: #E07B39 !important;
    box-shadow: 0 0 0 3px rgba(224, 123, 57, 0.08) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder {
    color: #3A3D47 !important;
}

/* ── Button ── */
.stButton > button {
    background-color: #E07B39 !important;
    color: #0E0F14 !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    height: 48px !important;
    width: 100% !important;
    letter-spacing: 0.02em;
    transition: background-color 0.15s ease, transform 0.1s ease;
}
.stButton > button:hover {
    background-color: #C9682A !important;
    transform: translateY(-1px);
}
.stButton > button:active {
    transform: translateY(0);
}

/* ── Status box ── */
[data-testid="stStatusWidget"] {
    background-color: #13141A !important;
    border: 1px solid #272930 !important;
    border-radius: 8px !important;
}

/* ── Metric cards ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 32px 0 28px 0;
}
.metric-card {
    background-color: #13141A;
    border: 1px solid #1E2028;
    border-radius: 8px;
    padding: 20px 24px;
}
.metric-card .m-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #3A3D47;
    margin-bottom: 8px;
}
.metric-card .m-value {
    font-size: 26px;
    font-weight: 700;
    color: #E8EAF0;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
}
.metric-card .m-value.accent { color: #E07B39; }
.metric-card .m-value.success { color: #4CAF7D; }

/* ── Divider ── */
.ie-divider {
    border: none;
    border-top: 1px solid #1E2028;
    margin: 32px 0;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid #1E2028;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 500;
    color: #606673;
    padding: 12px 20px;
    background: transparent;
    border-radius: 0;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
}
.stTabs [aria-selected="true"] {
    color: #E8EAF0 !important;
    border-bottom: 2px solid #E07B39 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 24px;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #1E2028;
    border-radius: 8px;
    overflow: hidden;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background-color: #1E2028 !important;
    color: #C9CDD6 !important;
    border: 1px solid #272930 !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background-color: #272930 !important;
    border-color: #3A3D47 !important;
}

/* ── Pipeline steps ── */
.pipeline-steps {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 28px;
    flex-wrap: wrap;
}
.pipeline-step {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-weight: 500;
    color: #3A3D47;
    letter-spacing: 0.04em;
}
.pipeline-step .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #272930;
}
.pipeline-step.active .dot { background-color: #E07B39; }
.pipeline-step.active { color: #C9CDD6; }
.pipeline-sep { color: #272930; font-size: 11px; }

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 64px 32px;
    border: 1px dashed #1E2028;
    border-radius: 8px;
    margin-top: 8px;
}
.empty-state .icon { font-size: 32px; margin-bottom: 16px; }
.empty-state h3 {
    font-size: 15px;
    font-weight: 600;
    color: #E8EAF0;
    margin: 0 0 8px 0;
}
.empty-state p {
    font-size: 13px;
    color: #606673;
    margin: 0;
    line-height: 1.6;
}

/* ── Info banner ── */
.info-banner {
    background-color: #13141A;
    border: 1px solid #1E2028;
    border-left: 3px solid #E07B39;
    border-radius: 0 6px 6px 0;
    padding: 12px 16px;
    font-size: 13px;
    color: #606673;
    margin-bottom: 24px;
}

/* ── Error ── */
.stAlert {
    border-radius: 6px !important;
    font-size: 13px !important;
}

/* ── Chart ── */
.stVegaLiteChart, [data-testid="stArrowVegaLiteChart"] {
    border: 1px solid #1E2028;
    border-radius: 8px;
    padding: 16px;
    background: #13141A;
}
</style>
""", unsafe_allow_html=True)

# ================= INIT PIPELINE =================
@st.cache_resource
def get_pipeline():
    return ExtractionPipeline()

pipeline = get_pipeline()

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("""
    <div style="padding: 8px 0;">
        <div style="font-size:11px; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; color:#3A3D47; margin-bottom:16px;">
            Tentang Sistem
        </div>
        <p style="font-size:13px; color:#606673; line-height:1.7; margin:0 0 24px 0;">
            Sistem ekstraksi informasi otomatis dari subtitle YouTube bengkel motor. 
            Mengidentifikasi relasi <strong style="color:#C9CDD6;">komponen → gejala → tindakan</strong> 
            dari narasi lisan teknisi.
        </p>
        <div style="font-size:11px; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; color:#3A3D47; margin-bottom:12px;">
            Pipeline
        </div>
    </div>
    """, unsafe_allow_html=True)

    steps = [
        ("⬇", "Unduh subtitle"),
        ("🧹", "Preprocessing"),
        ("🏷", "Weak supervision"),
        ("🔍", "Ekstraksi"),
        ("📋", "Triplet output"),
    ]
    for icon, label in steps:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; padding:8px 0; border-bottom:1px solid #1E2028;">
            <span style="font-size:14px;">{icon}</span>
            <span style="font-size:12px; color:#606673;">{label}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:32px; padding-top:24px; border-top:1px solid #1E2028;">
        <div style="font-size:11px; color:#3A3D47; margin-bottom:4px;">© 2026 · Skripsi</div>
        <div style="font-size:12px; color:#606673; font-weight:500;">Moch Afaldo Danny Ardiansyah</div>
    </div>
    """, unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<div class="ie-header">
    <div class="eyebrow">🔧 Bengkel Motor · Information Extraction</div>
    <h1>Ekstraksi Relasi Kerusakan<br>dari Subtitle YouTube</h1>
    <p class="subtitle">
        Masukkan tautan video YouTube bengkel motor — sistem akan mengidentifikasi 
        relasi triplet komponen, gejala, dan tindakan perbaikan secara otomatis.
    </p>
</div>
""", unsafe_allow_html=True)

# ================= INPUT =================
st.markdown('<div class="input-label">Tautan Video Target</div>', unsafe_allow_html=True)

col_input, col_btn = st.columns([5, 1])
with col_input:
    url_input = st.text_input(
        "url",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed"
    )
with col_btn:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    btn_process = st.button("Ekstrak →")

st.markdown('<hr class="ie-divider">', unsafe_allow_html=True)

# ================= EMPTY STATE =================
if not btn_process:
    st.markdown("""
    <div class="empty-state">
        <div class="icon">⚙️</div>
        <h3>Siap memproses video</h3>
        <p>Tempel tautan YouTube di atas, lalu klik <strong>Ekstrak →</strong><br>
        untuk menjalankan pipeline ekstraksi informasi.</p>
    </div>
    """, unsafe_allow_html=True)

# ================= EKSEKUSI =================
if btn_process:
    if not url_input or not url_input.strip().startswith("http"):
        st.error("Masukkan tautan YouTube yang valid (dimulai dengan https://).")
    else:
        with st.status("Menjalankan pipeline ekstraksi...", expanded=True) as status:
            try:
                start_time = time.time()

                st.text("① Mengunduh subtitle dari YouTube...")
                is_ready = pipeline.download_video(url_input)

                if not is_ready:
                    status.update(label="Subtitle tidak tersedia", state="error", expanded=False)
                    st.error(
                        "Video tidak memiliki subtitle atau caption otomatis dalam Bahasa Indonesia. "
                        "Coba video lain dari channel bengkel motor yang aktif."
                    )
                else:
                    st.text("② Membersihkan dan mensegmentasi teks...")
                    st.text("③ Menjalankan weak supervision & scoring kalimat...")
                    st.text("④ Mengekstrak relasi triplet (komponen → gejala/tindakan)...")
                    pipeline.run_full_pipeline()

                    status.update(label="Pipeline selesai", state="complete", expanded=False)
                    elapsed = time.time() - start_time

                    ROOT_DIR = Path(__file__).parent
                    result_path = ROOT_DIR / "data" / "processed" / "final_extraction" / "final_triplets_with_counts.csv"

                    if result_path.exists():
                        df = pd.read_csv(result_path)
                        total = len(df)

                        if total > 0:
                            # ── Metric cards ──
                            unique_subjects = df['subject'].nunique() if 'subject' in df.columns else 0
                            st.markdown(f"""
                            <div class="metric-grid">
                                <div class="metric-card">
                                    <div class="m-label">Relasi diekstrak</div>
                                    <div class="m-value accent">{total}</div>
                                </div>
                                <div class="metric-card">
                                    <div class="m-label">Komponen unik</div>
                                    <div class="m-value">{unique_subjects}</div>
                                </div>
                                <div class="metric-card">
                                    <div class="m-label">Waktu eksekusi</div>
                                    <div class="m-value success">{elapsed:.1f}s</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            # ── Tabs ──
                            tab_data, tab_viz, tab_export = st.tabs([
                                "Basis Pengetahuan",
                                "Distribusi Komponen",
                                "Ekspor Data"
                            ])

                            with tab_data:
                                st.markdown("""
                                <div class="info-banner">
                                    Setiap baris merepresentasikan satu relasi triplet: 
                                    <strong>komponen</strong> yang mengalami <strong>gejala</strong> 
                                    atau mendapat <strong>tindakan</strong> perbaikan.
                                </div>
                                """, unsafe_allow_html=True)
                                st.dataframe(
                                    df,
                                    use_container_width=True,
                                    hide_index=True,
                                    height=380,
                                    column_config={
                                        "subject": st.column_config.TextColumn("Komponen", width="medium"),
                                        "relation": st.column_config.TextColumn("Relasi", width="medium"),
                                        "object": st.column_config.TextColumn("Gejala / Tindakan", width="large"),
                                        "count": st.column_config.NumberColumn("Frekuensi", format="%d ×", width="small"),
                                    }
                                )

                            with tab_viz:
                                if 'subject' in df.columns:
                                    top_n = 15
                                    subject_counts = (
                                        df.groupby('subject')['count'].sum()
                                        .sort_values(ascending=False)
                                        .head(top_n)
                                        .reset_index()
                                    )
                                    subject_counts.columns = ['Komponen', 'Total Relasi']
                                    st.markdown(f"""
                                    <div style="font-size:12px; color:#606673; margin-bottom:16px;">
                                        Top {top_n} komponen berdasarkan total frekuensi relasi yang diekstrak
                                    </div>
                                    """, unsafe_allow_html=True)
                                    st.bar_chart(
                                        subject_counts.set_index('Komponen'),
                                        height=360,
                                        color="#E07B39"
                                    )
                                else:
                                    st.info("Kolom 'subject' tidak ditemukan pada data hasil.")

                            with tab_export:
                                st.markdown("""
                                <div class="info-banner">
                                    Data dalam format CSV — siap diimpor ke database atau 
                                    digunakan untuk analisis lebih lanjut.
                                </div>
                                """, unsafe_allow_html=True)

                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.download_button(
                                        label="⬇ Unduh CSV Lengkap",
                                        data=df.to_csv(index=False).encode('utf-8'),
                                        file_name=f"knowledge_base_otomotif.csv",
                                        mime="text/csv",
                                        use_container_width=True
                                    )
                                with col_b:
                                    # Hanya relasi dengan frekuensi > 1
                                    df_filtered = df[df['count'] > 1] if 'count' in df.columns else df
                                    st.download_button(
                                        label="⬇ Unduh CSV Terfilter (freq > 1)",
                                        data=df_filtered.to_csv(index=False).encode('utf-8'),
                                        file_name=f"knowledge_base_otomotif_filtered.csv",
                                        mime="text/csv",
                                        use_container_width=True
                                    )

                                st.markdown(f"""
                                <div style="margin-top:20px; font-size:12px; color:#3A3D47; font-family:'JetBrains Mono',monospace;">
                                    {total} baris · {len(df.columns)} kolom · {df_filtered.__len__()} relasi frekuensi > 1
                                </div>
                                """, unsafe_allow_html=True)

                        else:
                            st.markdown("""
                            <div class="empty-state">
                                <div class="icon">🔍</div>
                                <h3>Tidak ada relasi yang diekstrak</h3>
                                <p>Pipeline selesai berjalan, namun tidak ada kalimat yang melampaui 
                                skor ambang batas weak supervision.<br>
                                Coba video dengan konten teknis bengkel yang lebih spesifik.</p>
                            </div>
                            """, unsafe_allow_html=True)

                    else:
                        st.error(f"File output tidak ditemukan: `{result_path}`")

            except Exception as e:
                status.update(label="Pipeline error", state="error", expanded=False)
                st.error(f"**Error:** {str(e)}")
                st.markdown("""
                <div style="font-size:12px; color:#606673; margin-top:8px;">
                    Pastikan semua dependensi terinstal dan file seed tersedia di direktori root.
                </div>
                """, unsafe_allow_html=True)