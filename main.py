"""
main.py — AI Information Overload Filter
Redesigned UI: dark/light compatible, animated, scrollable priority panel.
"""

import streamlit as st

from preprocessing import preprocess
from summarizer    import summarize, LENGTH_PRESETS
from classifier    import classify_sentences, extract_key_insights
from utils         import (
    extract_keywords, read_txt_file, read_pdf_file,
    validate_file_size, truncate_text, MAX_FILE_SIZE_MB,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SmartFilter · AI Content Cleaner",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">

<style>
/* ═══════════════════════════════════════════
   CSS VARIABLES — auto light/dark via prefers
   ═══════════════════════════════════════════ */
:root {
  --bg:           #f0f2f8;
  --bg2:          #e4e8f2;
  --surface:      rgba(255,255,255,0.82);
  --surface2:     rgba(255,255,255,0.55);
  --border:       rgba(110,130,180,0.18);
  --text:         #1a1d2e;
  --text2:        #4a5080;
  --text3:        #8890b0;
  --accent:       #4f46e5;
  --accent2:      #06b6d4;
  --urgent:       #ef4444;
  --urgent-bg:    rgba(239,68,68,0.08);
  --important:    #f59e0b;
  --important-bg: rgba(245,158,11,0.08);
  --ignore:       #94a3b8;
  --ignore-bg:    rgba(148,163,184,0.06);
  --success:      #10b981;
  --glow:         rgba(79,70,229,0.15);
  --radius:       16px;
  --radius-sm:    10px;
  --shadow:       0 4px 24px rgba(0,0,0,0.08);
  --shadow-lg:    0 12px 48px rgba(0,0,0,0.12);
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg:           #090c18;
    --bg2:          #0f1220;
    --surface:      rgba(255,255,255,0.05);
    --surface2:     rgba(255,255,255,0.03);
    --border:       rgba(255,255,255,0.08);
    --text:         #e8ecff;
    --text2:        #8892c0;
    --text3:        #4a5280;
    --accent:       #818cf8;
    --accent2:      #22d3ee;
    --urgent:       #f87171;
    --urgent-bg:    rgba(248,113,113,0.1);
    --important:    #fbbf24;
    --important-bg: rgba(251,191,36,0.1);
    --ignore:       #475569;
    --ignore-bg:    rgba(71,85,105,0.12);
    --success:      #34d399;
    --glow:         rgba(129,140,248,0.2);
    --shadow:       0 4px 24px rgba(0,0,0,0.4);
    --shadow-lg:    0 12px 48px rgba(0,0,0,0.6);
  }
}

/* ═══════════════════════════════════════════
   STREAMLIT RESETS
   ═══════════════════════════════════════════ */
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
  background: var(--bg) !important;
  font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stHeader"]          { background: transparent !important; }
[data-testid="stSidebar"]         { background: var(--bg2) !important; }
[data-testid="stMainBlockContainer"] { padding-top: 0 !important; }
section[data-testid="stMain"] > div { padding-top: 0 !important; }
.block-container { padding: 0 2rem 2rem 2rem !important; max-width: 1400px !important; }

/* Remove default Streamlit bottom padding */
footer { display: none !important; }
#MainMenu { display: none !important; }

/* ═══════════════════════════════════════════
   TYPOGRAPHY
   ═══════════════════════════════════════════ */
h1,h2,h3,h4 {
  font-family: 'Syne', sans-serif !important;
  color: var(--text) !important;
}
p, li, div, span, label {
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
}

/* ═══════════════════════════════════════════
   ANIMATIONS
   ═══════════════════════════════════════════ */
@keyframes fadeUp {
  from { opacity:0; transform:translateY(20px); }
  to   { opacity:1; transform:translateY(0); }
}
@keyframes fadeIn {
  from { opacity:0; }
  to   { opacity:1; }
}
@keyframes slideRight {
  from { opacity:0; transform:translateX(-16px); }
  to   { opacity:1; transform:translateX(0); }
}
@keyframes pulse-ring {
  0%   { box-shadow: 0 0 0 0 rgba(239,68,68,0.35); }
  70%  { box-shadow: 0 0 0 8px rgba(239,68,68,0); }
  100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
}
@keyframes shimmer {
  0%   { background-position: -600px 0; }
  100% { background-position: 600px 0; }
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ═══════════════════════════════════════════
   HERO BANNER
   ═══════════════════════════════════════════ */
.hero {
  background: linear-gradient(135deg,
    var(--accent) 0%,
    var(--accent2) 100%);
  border-radius: 0 0 32px 32px;
  padding: 3rem 3rem 2.6rem;
  margin: 0 -2rem 2rem -2rem;
  position: relative;
  overflow: hidden;
  animation: fadeIn 0.6s ease;
}
.hero::before {
  content: '';
  position: absolute; inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}
.hero-title {
  font-family: 'Syne', sans-serif;
  font-size: 2.4rem;
  font-weight: 800;
  color: #fff !important;
  margin: 0 0 0.4rem 0;
  line-height: 1.1;
  letter-spacing: -0.5px;
}
.hero-sub {
  color: rgba(255,255,255,0.82) !important;
  font-size: 1.05rem;
  font-weight: 400;
  margin: 0;
}
.hero-badge {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.25);
  border-radius: 30px;
  padding: 4px 14px;
  font-size: 0.78rem;
  font-weight: 600;
  color: #fff !important;
  margin-bottom: 1rem;
  backdrop-filter: blur(8px);
}

/* ═══════════════════════════════════════════
   GLASS CARDS
   ═══════════════════════════════════════════ */
.glass-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.4rem 1.6rem;
  box-shadow: var(--shadow);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  transition: box-shadow 0.25s ease, transform 0.25s ease;
  animation: fadeUp 0.45s ease both;
}
.glass-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

/* ═══════════════════════════════════════════
   INPUT PANEL
   ═══════════════════════════════════════════ */
.input-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.6rem;
  box-shadow: var(--shadow);
  backdrop-filter: blur(12px);
  animation: fadeUp 0.5s ease both;
}

/* ═══════════════════════════════════════════
   STREAMLIT WIDGETS CUSTOM STYLE
   ═══════════════════════════════════════════ */
[data-testid="stTextArea"] textarea {
  background: var(--surface2) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.95rem !important;
  transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
  resize: vertical !important;
}
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--glow) !important;
  outline: none !important;
}
[data-testid="stFileUploader"] {
  background: var(--surface2) !important;
  border: 2px dashed var(--border) !important;
  border-radius: var(--radius-sm) !important;
  transition: border-color 0.2s ease !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--accent) !important;
}
[data-testid="stSelectbox"] > div,
[data-testid="stRadio"] {
  background: transparent !important;
}
.stButton > button {
  background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
  color: #fff !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
  font-size: 1rem !important;
  padding: 0.7rem 1.4rem !important;
  transition: opacity 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease !important;
  box-shadow: 0 4px 16px var(--glow) !important;
}
.stButton > button:hover {
  opacity: 0.9 !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 28px var(--glow) !important;
}
.stButton > button:active {
  transform: translateY(0) !important;
}

/* Labels */
[data-testid="stWidgetLabel"] p,
label[data-testid="stWidgetLabel"] {
  color: var(--text2) !important;
  font-size: 0.82rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.5px !important;
  text-transform: uppercase !important;
}

/* ═══════════════════════════════════════════
   STAT CHIPS
   ═══════════════════════════════════════════ */
.stats-row {
  display: flex; flex-wrap: wrap; gap: 10px;
  margin: 1rem 0 1.4rem;
  animation: fadeIn 0.5s ease both;
  animation-delay: 0.15s;
}
.stat-chip {
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 30px;
  padding: 5px 14px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--accent) !important;
  box-shadow: var(--shadow);
  animation: slideRight 0.4s ease both;
}

/* ═══════════════════════════════════════════
   SECTION HEADERS
   ═══════════════════════════════════════════ */
.section-header {
  display: flex; align-items: center; gap: 10px;
  margin: 1.6rem 0 0.9rem;
  animation: fadeUp 0.4s ease both;
}
.section-icon {
  width: 32px; height: 32px;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}
.section-title {
  font-family: 'Syne', sans-serif !important;
  font-size: 1.1rem !important;
  font-weight: 700 !important;
  color: var(--text) !important;
  margin: 0 !important;
}

/* ═══════════════════════════════════════════
   SUMMARY CARD
   ═══════════════════════════════════════════ */
.summary-card {
  background: linear-gradient(135deg,
    rgba(79,70,229,0.08) 0%,
    rgba(6,182,212,0.05) 100%);
  border: 1px solid rgba(79,70,229,0.2);
  border-radius: var(--radius);
  padding: 1.5rem 1.8rem;
  line-height: 1.75;
  font-size: 0.97rem;
  color: var(--text) !important;
  box-shadow: var(--shadow);
  animation: fadeUp 0.5s ease both;
  animation-delay: 0.1s;
  position: relative;
  overflow: hidden;
}
.summary-card::before {
  content: '';
  position: absolute; top:0; left:0;
  width: 4px; height: 100%;
  background: linear-gradient(180deg, var(--accent), var(--accent2));
}

/* ═══════════════════════════════════════════
   INSIGHT BULLETS
   ═══════════════════════════════════════════ */
.insight-item {
  display: flex; align-items: flex-start; gap: 10px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 0.8rem 1rem;
  margin-bottom: 8px;
  font-size: 0.9rem;
  color: var(--text) !important;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  animation: slideRight 0.4s ease both;
}
.insight-item:hover { transform: translateX(4px); box-shadow: var(--shadow); }
.insight-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  flex-shrink: 0; margin-top: 6px;
}

/* ═══════════════════════════════════════════
   KEYWORD PILLS
   ═══════════════════════════════════════════ */
.pill-wrap { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.pill {
  display: inline-flex; align-items: center;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text2) !important;
  transition: all 0.2s ease;
  cursor: default;
}
.pill:hover {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff !important;
  transform: scale(1.05);
}
.pill-entity {
  border-color: rgba(16,185,129,0.3);
  color: var(--success) !important;
}
.pill-entity:hover { background: var(--success); color: #fff !important; }

/* ═══════════════════════════════════════════
   PRIORITY PANEL — FIXED HEIGHT SCROLL
   ═══════════════════════════════════════════ */
.priority-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  overflow: hidden;
  display: flex; flex-direction: column;
  animation: fadeUp 0.5s ease both;
  animation-delay: 0.2s;
}
.priority-panel-header {
  padding: 1.1rem 1.4rem 0.8rem;
  border-bottom: 1px solid var(--border);
  background: var(--surface2);
  display: flex; align-items: center; justify-content: space-between;
}
.priority-panel-header h4 {
  font-family: 'Syne', sans-serif !important;
  font-size: 1rem !important;
  font-weight: 700 !important;
  margin: 0 !important;
  color: var(--text) !important;
}
.priority-scroll-area {
  max-height: 620px;
  overflow-y: auto;
  padding: 1rem;
  scrollbar-width: thin;
  scrollbar-color: var(--border) transparent;
}
.priority-scroll-area::-webkit-scrollbar { width: 5px; }
.priority-scroll-area::-webkit-scrollbar-track { background: transparent; }
.priority-scroll-area::-webkit-scrollbar-thumb {
  background: var(--border); border-radius: 10px;
}
.priority-group-label {
  display: flex; align-items: center; gap: 8px;
  font-family: 'Syne', sans-serif;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--text3) !important;
  margin: 1rem 0 0.5rem;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}
.priority-group-label:first-child { margin-top: 0; }

/* ═══════════════════════════════════════════
   SENTENCE CARDS
   ═══════════════════════════════════════════ */
.sent-card {
  border-radius: var(--radius-sm);
  padding: 0.75rem 1rem;
  margin-bottom: 7px;
  font-size: 0.88rem;
  line-height: 1.6;
  color: var(--text) !important;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  animation: fadeUp 0.35s ease both;
  position: relative;
}
.sent-card:hover { transform: translateX(3px); }
.sent-urgent {
  background: var(--urgent-bg);
  border-left: 3px solid var(--urgent);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  animation-name: fadeUp;
}
.sent-important {
  background: var(--important-bg);
  border-left: 3px solid var(--important);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}
.sent-ignore {
  background: var(--ignore-bg);
  border-left: 3px solid var(--ignore);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  opacity: 0.75;
}
.conf-row {
  display: flex; align-items: center; gap: 7px;
  margin-top: 6px;
}
.conf-label { font-size: 0.72rem; color: var(--text3) !important; font-weight: 500; }
.conf-track {
  flex: 1; height: 4px; background: var(--border);
  border-radius: 4px; overflow: hidden;
}
.conf-fill { height: 4px; border-radius: 4px; }

/* URGENT pulse badge */
.urgent-badge {
  display: inline-block;
  background: var(--urgent);
  color: #fff !important;
  font-size: 0.65rem; font-weight: 700;
  padding: 2px 7px; border-radius: 20px;
  letter-spacing: 0.5px;
  animation: pulse-ring 2s infinite;
  float: right; margin-top: 2px;
}
.important-badge {
  display: inline-block;
  background: var(--important);
  color: #fff !important;
  font-size: 0.65rem; font-weight: 700;
  padding: 2px 7px; border-radius: 20px;
  letter-spacing: 0.5px;
  float: right; margin-top: 2px;
}

/* ═══════════════════════════════════════════
   EMPTY STATE
   ═══════════════════════════════════════════ */
.empty-state {
  text-align: center; padding: 2rem 1rem;
  color: var(--text3) !important;
  font-size: 0.9rem;
}

/* ═══════════════════════════════════════════
   COUNT BADGES IN PANEL HEADER
   ═══════════════════════════════════════════ */
.count-badge {
  display: inline-flex; align-items: center; gap: 4px;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 20px; padding: 3px 10px;
  font-size: 0.75rem; font-weight: 600;
  margin-left: 4px;
}
.dot-urgent    { width:7px;height:7px;border-radius:50%;background:var(--urgent);display:inline-block; }
.dot-important { width:7px;height:7px;border-radius:50%;background:var(--important);display:inline-block; }
.dot-ignore    { width:7px;height:7px;border-radius:50%;background:var(--ignore);display:inline-block; }

/* ═══════════════════════════════════════════
   ALERTS / WARNINGS
   ═══════════════════════════════════════════ */
.alert-warn {
  background: rgba(245,158,11,0.1);
  border: 1px solid rgba(245,158,11,0.3);
  border-radius: var(--radius-sm); padding: 0.8rem 1rem;
  color: var(--important) !important; font-size: 0.9rem;
  margin-bottom: 1rem; display:flex; gap:8px; align-items:center;
}
.alert-info {
  background: rgba(79,70,229,0.08);
  border: 1px solid rgba(79,70,229,0.2);
  border-radius: var(--radius-sm); padding: 0.8rem 1rem;
  color: var(--accent) !important; font-size: 0.9rem;
  margin-bottom: 1rem; display:flex; gap:8px; align-items:center;
}
.alert-error {
  background: rgba(239,68,68,0.08);
  border: 1px solid rgba(239,68,68,0.25);
  border-radius: var(--radius-sm); padding: 0.8rem 1rem;
  color: var(--urgent) !important; font-size: 0.9rem;
  margin-bottom: 1rem;
}

/* ═══════════════════════════════════════════
   DIVIDER
   ═══════════════════════════════════════════ */
.divider {
  border: none; border-top: 1px solid var(--border);
  margin: 1.4rem 0;
}

/* ═══════════════════════════════════════════
   STACKED DELAY HELPERS
   ═══════════════════════════════════════════ */
.d1{animation-delay:0.05s} .d2{animation-delay:0.10s}
.d3{animation-delay:0.15s} .d4{animation-delay:0.20s}
.d5{animation-delay:0.25s} .d6{animation-delay:0.30s}

</style>
""", unsafe_allow_html=True)


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">⚡ Smart Content Intelligence</div>
  <div class="hero-title">Information Overload Filter</div>
  <p class="hero-sub">
    Drop any content — emails, reports, articles — and get a clean summary,
    priority labels, and key insights in seconds.
  </p>
</div>
""", unsafe_allow_html=True)


# ── Input + Options ────────────────────────────────────────────────────────────
col_in, col_opt = st.columns([3, 1], gap="large")

with col_in:
    st.markdown('<div class="input-panel">', unsafe_allow_html=True)

    mode = st.radio(
        "Input method",
        ["✍️  Type or Paste", "📂  Upload File"],
        horizontal=True,
        label_visibility="collapsed",
    )

    raw_text = ""

    if mode == "✍️  Type or Paste":
        raw_text = st.text_area(
            "Content",
            height=200,
            placeholder="Paste an email, meeting notes, article, report… anything.",
            label_visibility="collapsed",
        )
    else:
        up = st.file_uploader(
            "Upload",
            type=["txt", "pdf"],
            label_visibility="collapsed",
        )
        if up:
            if not validate_file_size(up):
                st.markdown(
                    f'<div class="alert-warn">⚠️ File exceeds {MAX_FILE_SIZE_MB} MB. Please upload a smaller file.</div>',
                    unsafe_allow_html=True,
                )
            else:
                try:
                    raw_text = read_pdf_file(up) if up.name.endswith(".pdf") else read_txt_file(up)
                    st.markdown(
                        f'<div class="alert-info">✓ Loaded <strong>{up.name}</strong> — {len(raw_text):,} characters</div>',
                        unsafe_allow_html=True,
                    )
                except ValueError as e:
                    st.markdown(f'<div class="alert-error">✕ {e}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with col_opt:
    st.markdown('<div class="glass-card" style="height:100%">', unsafe_allow_html=True)
    st.markdown("**⚙️ Options**")
    summary_length = st.selectbox("Summary length", list(LENGTH_PRESETS.keys()), index=1)
    show_ignored   = st.checkbox("Show low-priority sentences", value=False)
    st.markdown("<br>", unsafe_allow_html=True)
    process = st.button("⚡ Analyse Content", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)


# ── Processing ─────────────────────────────────────────────────────────────────
if process:
    if not raw_text or not raw_text.strip():
        st.markdown('<div class="alert-warn">⚠️ Please enter or upload some content first.</div>', unsafe_allow_html=True)
        st.stop()

    text, was_truncated = truncate_text(raw_text)
    if was_truncated:
        st.markdown(
            '<div class="alert-info">ℹ️ Input trimmed to 15,000 characters for performance.</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Preprocessing
    with st.spinner("Preprocessing…"):
        prep = preprocess(text)

    if prep["language"] != "en":
        st.markdown(
            '<div class="alert-warn">⚠️ Content may not be in English — accuracy may vary.</div>',
            unsafe_allow_html=True,
        )

    # Stat chips
    st.markdown(
        f"""<div class="stats-row">
            <span class="stat-chip d1">📝 {prep['word_count']:,} words</span>
            <span class="stat-chip d2">💬 {prep['sentence_count']} sentences</span>
            <span class="stat-chip d3">🌐 {prep['language'].upper()}</span>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── Two-column results ─────────────────────────────────────────────────────
    col_l, col_r = st.columns([1.65, 1], gap="large")

    # ── LEFT COLUMN ────────────────────────────────────────────────────────────
    with col_l:

        # Summary
        st.markdown(
            '<div class="section-header"><div class="section-icon">📋</div>'
            '<p class="section-title">Summary</p></div>',
            unsafe_allow_html=True,
        )
        with st.spinner("Generating summary — may take ~30 s on first run…"):
            sum_result = summarize(prep["cleaned_text"], length=summary_length)

        if sum_result.get("error"):
            st.markdown(
                f'<div class="alert-error">✕ Summarization error: {sum_result["error"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            if sum_result.get("note"):
                st.markdown(f'<div class="alert-info">ℹ️ {sum_result["note"]}</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="summary-card">{sum_result["summary"]}</div>',
                unsafe_allow_html=True,
            )

        # Key Insights
        st.markdown(
            '<div class="section-header"><div class="section-icon">💡</div>'
            '<p class="section-title">Key Insights</p></div>',
            unsafe_allow_html=True,
        )
        insights = extract_key_insights(prep["sentences"], top_n=6)
        if insights:
            bullets = "".join(
                f'<div class="insight-item d{min(i+1,6)}">'
                f'<div class="insight-dot"></div>{s}</div>'
                for i, s in enumerate(insights)
            )
            st.markdown(bullets, unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state">No key insights found.</div>', unsafe_allow_html=True)

        # Keywords
        st.markdown(
            '<div class="section-header"><div class="section-icon">🔑</div>'
            '<p class="section-title">Keywords & Entities</p></div>',
            unsafe_allow_html=True,
        )
        with st.spinner("Extracting keywords…"):
            kw = extract_keywords(prep["cleaned_text"])

        if kw.get("error"):
            st.markdown(f'<div class="alert-warn">⚠️ {kw["error"]}</div>', unsafe_allow_html=True)
        else:
            if kw["entities"]:
                pills = " ".join(
                    f'<span class="pill pill-entity">{e}</span>' for e in kw["entities"]
                )
                st.markdown(
                    f'<div class="glass-card" style="margin-bottom:10px">'
                    f'<p style="font-size:0.75rem;font-weight:700;letter-spacing:0.5px;'
                    f'text-transform:uppercase;color:var(--text3);margin:0 0 10px">Named Entities</p>'
                    f'<div class="pill-wrap">{pills}</div></div>',
                    unsafe_allow_html=True,
                )
            if kw["noun_phrases"]:
                pills = " ".join(
                    f'<span class="pill">{p}</span>' for p in kw["noun_phrases"]
                )
                st.markdown(
                    f'<div class="glass-card">'
                    f'<p style="font-size:0.75rem;font-weight:700;letter-spacing:0.5px;'
                    f'text-transform:uppercase;color:var(--text3);margin:0 0 10px">Key Phrases</p>'
                    f'<div class="pill-wrap">{pills}</div></div>',
                    unsafe_allow_html=True,
                )

    # ── RIGHT COLUMN — Prioritized Sentences (fixed scroll) ────────────────────
    with col_r:
        with st.spinner("Classifying sentences…"):
            classified = classify_sentences(prep["sentences"])

        urgent_items    = classified["URGENT"]
        important_items = classified["IMPORTANT"]
        ignore_items    = classified["IGNORE"]

        def conf_bar(conf: float, color: str) -> str:
            pct = int(conf * 100)
            return (
                f'<div class="conf-row">'
                f'<span class="conf-label">Confidence {pct}%</span>'
                f'<div class="conf-track">'
                f'<div class="conf-fill" style="width:{pct}%;background:{color}"></div>'
                f'</div></div>'
            )

        # Build the scrollable inner HTML
        inner = ""

        # URGENT group
        inner += (
            f'<div class="priority-group-label">'
            f'<span class="dot-urgent"></span> Urgent'
            f'<span style="margin-left:auto;font-size:0.75rem;'
            f'color:var(--urgent)">{len(urgent_items)}</span></div>'
        )
        if urgent_items:
            for item in urgent_items:
                inner += (
                    f'<div class="sent-card sent-urgent">'
                    f'<span class="urgent-badge">URGENT</span>'
                    f'{item["sentence"]}'
                    f'{conf_bar(item["confidence"], "var(--urgent)")}'
                    f'</div>'
                )
        else:
            inner += '<div class="empty-state" style="padding:0.5rem 0 1rem">No urgent items found.</div>'

        # IMPORTANT group
        inner += (
            f'<div class="priority-group-label">'
            f'<span class="dot-important"></span> Important'
            f'<span style="margin-left:auto;font-size:0.75rem;'
            f'color:var(--important)">{len(important_items)}</span></div>'
        )
        if important_items:
            for item in important_items:
                inner += (
                    f'<div class="sent-card sent-important">'
                    f'<span class="important-badge">ACTION</span>'
                    f'{item["sentence"]}'
                    f'{conf_bar(item["confidence"], "var(--important)")}'
                    f'</div>'
                )
        else:
            inner += '<div class="empty-state" style="padding:0.5rem 0 1rem">No important items found.</div>'

        # IGNORE group (optional)
        if show_ignored:
            inner += (
                f'<div class="priority-group-label">'
                f'<span class="dot-ignore"></span> Low Priority'
                f'<span style="margin-left:auto;font-size:0.75rem;'
                f'color:var(--ignore)">{len(ignore_items)}</span></div>'
            )
            for item in ignore_items[:25]:
                inner += (
                    f'<div class="sent-card sent-ignore">'
                    f'{item["sentence"]}'
                    f'</div>'
                )

        # Total summary row for panel header
        total = len(urgent_items) + len(important_items) + len(ignore_items)
        header_badges = (
            f'<span class="count-badge"><span class="dot-urgent"></span>{len(urgent_items)}</span>'
            f'<span class="count-badge"><span class="dot-important"></span>{len(important_items)}</span>'
        )
        if show_ignored:
            header_badges += f'<span class="count-badge"><span class="dot-ignore"></span>{len(ignore_items)}</span>'

        st.markdown(
            f'<div class="priority-panel">'
            f'<div class="priority-panel-header">'
            f'<h4>🗂️ Prioritized Sentences</h4>'
            f'<div>{header_badges}</div>'
            f'</div>'
            f'<div class="priority-scroll-area">{inner}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
