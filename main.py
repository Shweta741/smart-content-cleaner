"""
main.py — AI Information Overload Filter
- Manual dark/light toggle via session state + JS
- Fixed input field text/background visibility
- Animated, glassmorphism UI
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

# ── Theme state ────────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

IS_DARK = st.session_state.theme == "dark"

# ── CSS variables per theme ────────────────────────────────────────────────────
if IS_DARK:
    V = {
        "bg":           "#090c18",
        "bg2":          "#0f1220",
        "surface":      "rgba(255,255,255,0.055)",
        "surface2":     "rgba(255,255,255,0.03)",
        "border":       "rgba(255,255,255,0.09)",
        "text":         "#e8ecff",
        "text2":        "#8892c0",
        "text3":        "#4a5280",
        "input_bg":     "#161928",
        "input_text":   "#e8ecff",
        "input_border": "rgba(255,255,255,0.12)",
        "accent":       "#818cf8",
        "accent2":      "#22d3ee",
        "urgent":       "#f87171",
        "urgent_bg":    "rgba(248,113,113,0.10)",
        "important":    "#fbbf24",
        "important_bg": "rgba(251,191,36,0.10)",
        "ignore":       "#475569",
        "ignore_bg":    "rgba(71,85,105,0.12)",
        "success":      "#34d399",
        "glow":         "rgba(129,140,248,0.20)",
        "shadow":       "0 4px 24px rgba(0,0,0,0.45)",
        "shadow_lg":    "0 12px 48px rgba(0,0,0,0.65)",
        "toggle_icon":  "☀️",
        "toggle_label": "Light mode",
    }
else:
    V = {
        "bg":           "#f0f2f8",
        "bg2":          "#e4e8f2",
        "surface":      "rgba(255,255,255,0.90)",
        "surface2":     "rgba(255,255,255,0.60)",
        "border":       "rgba(110,130,180,0.18)",
        "text":         "#1a1d2e",
        "text2":        "#4a5080",
        "text3":        "#8890b0",
        "input_bg":     "#ffffff",
        "input_text":   "#1a1d2e",
        "input_border": "rgba(110,130,180,0.28)",
        "accent":       "#4f46e5",
        "accent2":      "#06b6d4",
        "urgent":       "#ef4444",
        "urgent_bg":    "rgba(239,68,68,0.07)",
        "important":    "#f59e0b",
        "important_bg": "rgba(245,158,11,0.07)",
        "ignore":       "#94a3b8",
        "ignore_bg":    "rgba(148,163,184,0.06)",
        "success":      "#10b981",
        "glow":         "rgba(79,70,229,0.14)",
        "shadow":       "0 4px 24px rgba(0,0,0,0.08)",
        "shadow_lg":    "0 12px 48px rgba(0,0,0,0.14)",
        "toggle_icon":  "🌙",
        "toggle_label": "Dark mode",
    }

# ── Inject CSS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<style>

/* ══════════════════════════════════════════════
   THEME VARIABLES
   ══════════════════════════════════════════════ */
:root {{
  --bg:           {V['bg']};
  --bg2:          {V['bg2']};
  --surface:      {V['surface']};
  --surface2:     {V['surface2']};
  --border:       {V['border']};
  --text:         {V['text']};
  --text2:        {V['text2']};
  --text3:        {V['text3']};
  --input-bg:     {V['input_bg']};
  --input-text:   {V['input_text']};
  --input-border: {V['input_border']};
  --accent:       {V['accent']};
  --accent2:      {V['accent2']};
  --urgent:       {V['urgent']};
  --urgent-bg:    {V['urgent_bg']};
  --important:    {V['important']};
  --important-bg: {V['important_bg']};
  --ignore:       {V['ignore']};
  --ignore-bg:    {V['ignore_bg']};
  --success:      {V['success']};
  --glow:         {V['glow']};
  --shadow:       {V['shadow']};
  --shadow-lg:    {V['shadow_lg']};
  --radius:       16px;
  --radius-sm:    10px;
}}

/* ══════════════════════════════════════════════
   STREAMLIT LAYOUT RESETS
   ══════════════════════════════════════════════ */
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {{
  background: var(--bg) !important;
  font-family: 'DM Sans', sans-serif !important;
}}
[data-testid="stHeader"]           {{ background: transparent !important; box-shadow: none !important; }}
[data-testid="stSidebar"]          {{ background: var(--bg2) !important; }}
[data-testid="stMainBlockContainer"] {{ padding-top: 0 !important; }}
section[data-testid="stMain"] > div {{ padding-top: 0 !important; }}
.block-container {{ padding: 0 2rem 2rem 2rem !important; max-width: 1440px !important; }}
footer {{ display: none !important; }}
#MainMenu {{ display: none !important; }}

/* ══════════════════════════════════════════════
   TYPOGRAPHY
   ══════════════════════════════════════════════ */
h1,h2,h3,h4,h5 {{
  font-family: 'Syne', sans-serif !important;
  color: var(--text) !important;
}}
p, li, span, div, label, small {{
  font-family: 'DM Sans', sans-serif !important;
  color: var(--text) !important;
}}

/* ══════════════════════════════════════════════
   INPUT FIELDS — COMPREHENSIVE FIX
   ══════════════════════════════════════════════ */

/* Textarea */
textarea,
[data-testid="stTextArea"] textarea,
[data-baseweb="textarea"] textarea,
.stTextArea textarea {{
  background-color: var(--input-bg) !important;
  color: var(--input-text) !important;
  border: 1.5px solid var(--input-border) !important;
  border-radius: var(--radius-sm) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.95rem !important;
  caret-color: var(--accent) !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}}
textarea:focus,
[data-testid="stTextArea"] textarea:focus {{
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--glow) !important;
  outline: none !important;
}}
textarea::placeholder {{
  color: var(--text3) !important;
  opacity: 1 !important;
}}

/* Select / Dropdown */
[data-baseweb="select"] > div,
[data-baseweb="select"] input,
[data-testid="stSelectbox"] > div > div,
.stSelectbox [data-baseweb="select"] div {{
  background-color: var(--input-bg) !important;
  color: var(--input-text) !important;
  border-color: var(--input-border) !important;
}}
[data-baseweb="select"] svg {{ fill: var(--text2) !important; }}

/* Dropdown menu list */
[data-baseweb="popover"] ul,
[data-baseweb="menu"],
[role="listbox"] {{
  background-color: var(--input-bg) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
}}
[role="option"] {{
  color: var(--input-text) !important;
  background: transparent !important;
}}
[role="option"]:hover,
[role="option"][aria-selected="true"] {{
  background-color: var(--glow) !important;
  color: var(--accent) !important;
}}

/* Radio buttons */
[data-testid="stRadio"] label,
[data-testid="stRadio"] p {{
  color: var(--text) !important;
}}
[data-testid="stRadio"] [data-baseweb="radio"] div {{
  border-color: var(--accent) !important;
}}

/* Checkbox */
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] p {{
  color: var(--text) !important;
}}
[data-testid="stCheckbox"] [data-baseweb="checkbox"] {{
  border-color: var(--accent) !important;
  background-color: var(--input-bg) !important;
}}

/* File uploader */
[data-testid="stFileUploader"],
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploaderDropzone"] {{
  background-color: var(--input-bg) !important;
  border: 2px dashed var(--input-border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text) !important;
}}
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small {{
  color: var(--text2) !important;
}}
[data-testid="stFileUploader"] button {{
  background: var(--surface) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
}}
[data-testid="stFileUploader"] svg {{
  fill: var(--text2) !important;
}}

/* Widget labels (SELECT, RADIO, etc.) */
[data-testid="stWidgetLabel"] p {{
  color: var(--text2) !important;
  font-size: 0.78rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.5px !important;
  text-transform: uppercase !important;
}}

/* Alert / info / warning native Streamlit boxes */
[data-testid="stAlert"] {{
  background: var(--surface) !important;
  color: var(--text) !important;
  border-radius: var(--radius-sm) !important;
}}

/* Spinner text */
[data-testid="stSpinner"] p {{ color: var(--text2) !important; }}

/* ══════════════════════════════════════════════
   PROCESS BUTTON
   ══════════════════════════════════════════════ */
.stButton > button {{
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
  font-size: 0.98rem !important;
  padding: 0.68rem 1.4rem !important;
  box-shadow: 0 4px 18px var(--glow) !important;
  transition: opacity 0.2s, transform 0.15s, box-shadow 0.2s !important;
  letter-spacing: 0.3px !important;
}}
.stButton > button:hover {{
  opacity: 0.88 !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 28px var(--glow) !important;
}}
.stButton > button:active {{ transform: translateY(0px) !important; }}

/* ══════════════════════════════════════════════
   ANIMATIONS
   ══════════════════════════════════════════════ */
@keyframes fadeUp {{
  from {{ opacity:0; transform:translateY(18px); }}
  to   {{ opacity:1; transform:translateY(0); }}
}}
@keyframes fadeIn {{
  from {{ opacity:0; }}
  to   {{ opacity:1; }}
}}
@keyframes slideRight {{
  from {{ opacity:0; transform:translateX(-14px); }}
  to   {{ opacity:1; transform:translateX(0); }}
}}
@keyframes pulse-ring {{
  0%   {{ box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }}
  70%  {{ box-shadow: 0 0 0 7px rgba(239,68,68,0); }}
  100% {{ box-shadow: 0 0 0 0 rgba(239,68,68,0); }}
}}
.d1{{animation-delay:.04s}} .d2{{animation-delay:.09s}}
.d3{{animation-delay:.14s}} .d4{{animation-delay:.19s}}
.d5{{animation-delay:.24s}} .d6{{animation-delay:.29s}}

/* ══════════════════════════════════════════════
   HERO BANNER
   ══════════════════════════════════════════════ */
.hero {{
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
  border-radius: 0 0 28px 28px;
  padding: 2.4rem 2.8rem 2.2rem;
  margin: 0 -2rem 1.8rem -2rem;
  position: relative; overflow: hidden;
  animation: fadeIn 0.5s ease;
}}
.hero::before {{
  content: '';
  position: absolute; inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='52' height='52' viewBox='0 0 52 52' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.055'%3E%3Ccircle cx='26' cy='26' r='2'/%3E%3C/g%3E%3C/svg%3E");
  pointer-events: none;
}}
.hero-inner {{
  display: flex; align-items: flex-start; justify-content: space-between;
  flex-wrap: wrap; gap: 1rem; position: relative; z-index: 1;
}}
.hero-text {{ flex: 1; min-width: 260px; }}
.hero-badge {{
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.28);
  border-radius: 30px; padding: 4px 14px;
  font-size: 0.76rem; font-weight: 600;
  color: #fff !important; margin-bottom: 0.8rem;
  letter-spacing: 0.4px;
}}
.hero-title {{
  font-family: 'Syne', sans-serif;
  font-size: 2.2rem; font-weight: 800;
  color: #fff !important; margin: 0 0 0.35rem;
  line-height: 1.1; letter-spacing: -0.5px;
}}
.hero-sub {{
  color: rgba(255,255,255,0.80) !important;
  font-size: 1rem; font-weight: 400; margin: 0;
}}
.theme-btn {{
  display: inline-flex; align-items: center; gap: 7px;
  background: rgba(255,255,255,0.18);
  border: 1.5px solid rgba(255,255,255,0.32);
  border-radius: 30px; padding: 8px 18px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.85rem; font-weight: 600;
  color: #fff !important; cursor: pointer;
  transition: background 0.2s, transform 0.15s;
  backdrop-filter: blur(8px);
  text-decoration: none; white-space: nowrap;
  align-self: flex-start;
}}
.theme-btn:hover {{
  background: rgba(255,255,255,0.28);
  transform: scale(1.04);
}}

/* ══════════════════════════════════════════════
   GLASS CARDS
   ══════════════════════════════════════════════ */
.glass-card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.4rem 1.6rem;
  box-shadow: var(--shadow);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  transition: box-shadow 0.25s, transform 0.25s;
  animation: fadeUp 0.45s ease both;
}}
.glass-card:hover {{
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}}
.input-panel {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.4rem 1.6rem;
  box-shadow: var(--shadow);
  backdrop-filter: blur(14px);
  animation: fadeUp 0.5s ease both;
}}

/* ══════════════════════════════════════════════
   STATS ROW
   ══════════════════════════════════════════════ */
.stats-row {{
  display: flex; flex-wrap: wrap; gap: 9px;
  margin: 1rem 0 1.4rem;
  animation: fadeIn 0.5s ease both;
}}
.stat-chip {{
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 30px; padding: 5px 14px;
  font-size: 0.81rem; font-weight: 600;
  color: var(--accent) !important;
  box-shadow: var(--shadow);
}}

/* ══════════════════════════════════════════════
   SECTION HEADERS
   ══════════════════════════════════════════════ */
.section-header {{
  display: flex; align-items: center; gap: 10px;
  margin: 1.5rem 0 0.85rem;
  animation: fadeUp 0.4s ease both;
}}
.section-icon {{
  width: 30px; height: 30px;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.9rem; flex-shrink: 0;
}}
.section-title {{
  font-family: 'Syne', sans-serif !important;
  font-size: 1.05rem !important;
  font-weight: 700 !important;
  color: var(--text) !important;
  margin: 0 !important;
}}

/* ══════════════════════════════════════════════
   SUMMARY CARD
   ══════════════════════════════════════════════ */
.summary-card {{
  background: {'rgba(129,140,248,0.07)' if IS_DARK else 'rgba(79,70,229,0.05)'};
  border: 1px solid {'rgba(129,140,248,0.18)' if IS_DARK else 'rgba(79,70,229,0.15)'};
  border-radius: var(--radius);
  padding: 1.4rem 1.6rem 1.4rem 1.9rem;
  line-height: 1.78; font-size: 0.96rem;
  color: var(--text) !important;
  box-shadow: var(--shadow);
  animation: fadeUp 0.5s ease both;
  animation-delay: 0.1s;
  position: relative; overflow: hidden;
}}
.summary-card::before {{
  content: '';
  position: absolute; top:0; left:0;
  width: 4px; height: 100%;
  background: linear-gradient(180deg, var(--accent), var(--accent2));
}}

/* ══════════════════════════════════════════════
   INSIGHT ITEMS
   ══════════════════════════════════════════════ */
.insight-item {{
  display: flex; align-items: flex-start; gap: 10px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 0.78rem 1rem;
  margin-bottom: 7px;
  font-size: 0.9rem; color: var(--text) !important;
  transition: transform 0.2s, box-shadow 0.2s;
  animation: slideRight 0.4s ease both;
}}
.insight-item:hover {{ transform: translateX(4px); box-shadow: var(--shadow); }}
.insight-dot {{
  width: 8px; height: 8px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  flex-shrink: 0; margin-top: 6px;
}}

/* ══════════════════════════════════════════════
   KEYWORD PILLS
   ══════════════════════════════════════════════ */
.pill-wrap {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }}
.pill {{
  display: inline-flex; align-items: center;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 20px; padding: 4px 12px;
  font-size: 0.79rem; font-weight: 500;
  color: var(--text2) !important;
  transition: all 0.18s ease; cursor: default;
}}
.pill:hover {{
  background: var(--accent); border-color: var(--accent);
  color: #fff !important; transform: scale(1.05);
}}
.pill-entity {{ border-color: {'rgba(52,211,153,0.3)' if IS_DARK else 'rgba(16,185,129,0.25)'}; color: var(--success) !important; }}
.pill-entity:hover {{ background: var(--success); color: #fff !important; border-color: var(--success); }}

/* ══════════════════════════════════════════════
   PRIORITY PANEL
   ══════════════════════════════════════════════ */
.priority-panel {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  overflow: hidden;
  display: flex; flex-direction: column;
  animation: fadeUp 0.5s ease both;
  animation-delay: 0.2s;
}}
.priority-panel-header {{
  padding: 1rem 1.4rem 0.85rem;
  border-bottom: 1px solid var(--border);
  background: var(--surface2);
  display: flex; align-items: center; justify-content: space-between;
}}
.priority-panel-header h4 {{
  font-family: 'Syne', sans-serif !important;
  font-size: 0.98rem !important; font-weight: 700 !important;
  margin: 0 !important; color: var(--text) !important;
}}
.priority-scroll-area {{
  max-height: 630px; overflow-y: auto; padding: 1rem;
  scrollbar-width: thin; scrollbar-color: var(--border) transparent;
}}
.priority-scroll-area::-webkit-scrollbar {{ width: 5px; }}
.priority-scroll-area::-webkit-scrollbar-track {{ background: transparent; }}
.priority-scroll-area::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 10px; }}

.priority-group-label {{
  display: flex; align-items: center; gap: 8px;
  font-family: 'Syne', sans-serif;
  font-size: 0.74rem; font-weight: 700;
  letter-spacing: 1.1px; text-transform: uppercase;
  color: var(--text3) !important;
  margin: 1rem 0 0.55rem;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}}
.priority-group-label:first-child {{ margin-top: 0; }}

/* ══════════════════════════════════════════════
   SENTENCE CARDS
   ══════════════════════════════════════════════ */
.sent-card {{
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  padding: 0.72rem 0.95rem;
  margin-bottom: 7px;
  font-size: 0.87rem; line-height: 1.62;
  color: var(--text) !important;
  transition: transform 0.18s;
  animation: fadeUp 0.35s ease both;
  position: relative;
}}
.sent-card:hover {{ transform: translateX(3px); }}
.sent-urgent   {{ background: var(--urgent-bg);   border-left: 3px solid var(--urgent); }}
.sent-important{{ background: var(--important-bg); border-left: 3px solid var(--important); }}
.sent-ignore   {{ background: var(--ignore-bg);   border-left: 3px solid var(--ignore); opacity: 0.72; }}

.conf-row {{
  display: flex; align-items: center; gap: 7px; margin-top: 6px;
}}
.conf-label {{ font-size: 0.70rem; color: var(--text3) !important; font-weight: 500; }}
.conf-track {{ flex:1; height:3px; background:var(--border); border-radius:4px; overflow:hidden; }}
.conf-fill  {{ height:3px; border-radius:4px; }}

.urgent-badge {{
  float: right; margin: 1px 0 4px 6px;
  background: var(--urgent); color:#fff !important;
  font-size: 0.63rem; font-weight:700;
  padding: 2px 8px; border-radius: 20px;
  letter-spacing: 0.5px;
  animation: pulse-ring 2.2s infinite;
}}
.important-badge {{
  float: right; margin: 1px 0 4px 6px;
  background: var(--important); color:#fff !important;
  font-size: 0.63rem; font-weight:700;
  padding: 2px 8px; border-radius: 20px;
  letter-spacing: 0.5px;
}}

/* ══════════════════════════════════════════════
   COUNT BADGES & DOTS
   ══════════════════════════════════════════════ */
.count-badge {{
  display: inline-flex; align-items: center; gap: 4px;
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: 20px; padding: 3px 10px;
  font-size: 0.73rem; font-weight: 600; margin-left: 4px;
  color: var(--text2) !important;
}}
.dot-u {{ width:6px;height:6px;border-radius:50%;background:var(--urgent);    display:inline-block; }}
.dot-i {{ width:6px;height:6px;border-radius:50%;background:var(--important); display:inline-block; }}
.dot-g {{ width:6px;height:6px;border-radius:50%;background:var(--ignore);    display:inline-block; }}

/* ══════════════════════════════════════════════
   INLINE ALERTS
   ══════════════════════════════════════════════ */
.al-warn {{
  background:rgba(245,158,11,0.10); border:1px solid rgba(245,158,11,0.28);
  border-radius:var(--radius-sm); padding:.8rem 1rem; margin-bottom:.9rem;
  color:var(--important)!important; font-size:.88rem;
  display:flex; gap:8px; align-items:center;
}}
.al-info {{
  background:rgba(79,70,229,0.08); border:1px solid rgba(79,70,229,0.2);
  border-radius:var(--radius-sm); padding:.8rem 1rem; margin-bottom:.9rem;
  color:var(--accent)!important; font-size:.88rem;
  display:flex; gap:8px; align-items:center;
}}
.al-err {{
  background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.22);
  border-radius:var(--radius-sm); padding:.8rem 1rem; margin-bottom:.9rem;
  color:var(--urgent)!important; font-size:.88rem;
}}
.al-info strong, .al-warn strong {{ color:inherit!important; }}

/* ══════════════════════════════════════════════
   MISC
   ══════════════════════════════════════════════ */
.divider {{ border:none; border-top:1px solid var(--border); margin:1.4rem 0; }}
.empty-state {{
  text-align:center; padding:1.5rem 1rem;
  color:var(--text3)!important; font-size:.88rem;
}}
.kw-subhead {{
  font-size:.73rem; font-weight:700; letter-spacing:.5px;
  text-transform:uppercase; color:var(--text3)!important;
  margin:0 0 10px;
}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════
toggle_icon  = V["toggle_icon"]
toggle_label = V["toggle_label"]

st.markdown(f"""
<div class="hero">
  <div class="hero-inner">
    <div class="hero-text">
      <div class="hero-badge">⚡ Smart Content Intelligence</div>
      <div class="hero-title">Information Overload Filter</div>
      <p class="hero-sub">Drop any content — emails, reports, articles — and get a clean
      summary, priority labels, and key insights in seconds.</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Theme toggle button — rendered just below hero via Streamlit column
_, btn_col = st.columns([8, 1])
with btn_col:
    st.button(
        f"{toggle_icon}  {toggle_label}",
        on_click=toggle_theme,
        key="theme_toggle",
        help="Switch between dark and light mode",
    )


# ══════════════════════════════════════════════
#  INPUT + OPTIONS
# ══════════════════════════════════════════════
col_in, col_opt = st.columns([3, 1], gap="large")

with col_in:
    st.markdown('<div class="input-panel">', unsafe_allow_html=True)
    mode = st.radio(
        "Input method",
        ["✍️  Type or Paste", "📂  Upload File"],
        horizontal=True, label_visibility="collapsed",
    )
    raw_text = ""
    if mode == "✍️  Type or Paste":
        raw_text = st.text_area(
            "Content", height=200,
            placeholder="Paste an email, meeting notes, article, report… anything.",
            label_visibility="collapsed",
        )
    else:
        up = st.file_uploader("Upload", type=["txt", "pdf"], label_visibility="collapsed")
        if up:
            if not validate_file_size(up):
                st.markdown(
                    f'<div class="al-warn">⚠️ File exceeds {MAX_FILE_SIZE_MB} MB. Upload a smaller file.</div>',
                    unsafe_allow_html=True,
                )
            else:
                try:
                    raw_text = read_pdf_file(up) if up.name.endswith(".pdf") else read_txt_file(up)
                    st.markdown(
                        f'<div class="al-info">✓ Loaded <strong>{up.name}</strong> — {len(raw_text):,} characters</div>',
                        unsafe_allow_html=True,
                    )
                except ValueError as e:
                    st.markdown(f'<div class="al-err">✕ {e}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_opt:
    st.markdown('<div class="glass-card" style="height:100%;">', unsafe_allow_html=True)
    st.markdown("**⚙️ Options**")
    summary_length = st.selectbox("Summary length", list(LENGTH_PRESETS.keys()), index=1)
    show_ignored   = st.checkbox("Show low-priority sentences", value=False)
    st.markdown("<br>", unsafe_allow_html=True)
    process = st.button("⚡ Analyse Content", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  PROCESSING
# ══════════════════════════════════════════════
if process:
    if not raw_text or not raw_text.strip():
        st.markdown('<div class="al-warn">⚠️ Please enter or upload some content first.</div>', unsafe_allow_html=True)
        st.stop()

    text, was_truncated = truncate_text(raw_text)
    if was_truncated:
        st.markdown(
            '<div class="al-info">ℹ️ Input trimmed to 15,000 characters for performance.</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    with st.spinner("Preprocessing…"):
        prep = preprocess(text)

    if prep["language"] != "en":
        st.markdown(
            '<div class="al-warn">⚠️ Content may not be in English — accuracy may vary.</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""<div class="stats-row">
            <span class="stat-chip d1">📝 {prep['word_count']:,} words</span>
            <span class="stat-chip d2">💬 {prep['sentence_count']} sentences</span>
            <span class="stat-chip d3">🌐 {prep['language'].upper()}</span>
        </div>""",
        unsafe_allow_html=True,
    )

    col_l, col_r = st.columns([1.65, 1], gap="large")

    # ── LEFT ──────────────────────────────────────────────────────────────────
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
            st.markdown(f'<div class="al-err">✕ {sum_result["error"]}</div>', unsafe_allow_html=True)
        else:
            if sum_result.get("note"):
                st.markdown(f'<div class="al-info">ℹ️ {sum_result["note"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="summary-card">{sum_result["summary"]}</div>', unsafe_allow_html=True)

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
            st.markdown('<div class="empty-state">No key insights extracted.</div>', unsafe_allow_html=True)

        # Keywords
        st.markdown(
            '<div class="section-header"><div class="section-icon">🔑</div>'
            '<p class="section-title">Keywords & Entities</p></div>',
            unsafe_allow_html=True,
        )
        with st.spinner("Extracting keywords…"):
            kw = extract_keywords(prep["cleaned_text"])

        if kw.get("error"):
            st.markdown(f'<div class="al-warn">⚠️ {kw["error"]}</div>', unsafe_allow_html=True)
        else:
            if kw["entities"]:
                pills = " ".join(f'<span class="pill pill-entity">{e}</span>' for e in kw["entities"])
                st.markdown(
                    f'<div class="glass-card" style="margin-bottom:10px">'
                    f'<p class="kw-subhead">Named Entities</p>'
                    f'<div class="pill-wrap">{pills}</div></div>',
                    unsafe_allow_html=True,
                )
            if kw["noun_phrases"]:
                pills = " ".join(f'<span class="pill">{p}</span>' for p in kw["noun_phrases"])
                st.markdown(
                    f'<div class="glass-card">'
                    f'<p class="kw-subhead">Key Phrases</p>'
                    f'<div class="pill-wrap">{pills}</div></div>',
                    unsafe_allow_html=True,
                )

    # ── RIGHT — priority panel ─────────────────────────────────────────────────
    with col_r:
        with st.spinner("Classifying sentences…"):
            classified = classify_sentences(prep["sentences"])

        urgent_items    = classified["URGENT"]
        important_items = classified["IMPORTANT"]
        ignore_items    = classified["IGNORE"]

        def conf_bar(conf, color):
            pct = int(conf * 100)
            return (
                f'<div class="conf-row">'
                f'<span class="conf-label">Confidence {pct}%</span>'
                f'<div class="conf-track">'
                f'<div class="conf-fill" style="width:{pct}%;background:{color}"></div>'
                f'</div></div>'
            )

        inner = ""

        inner += (
            f'<div class="priority-group-label">'
            f'<span class="dot-u"></span> Urgent'
            f'<span style="margin-left:auto;color:var(--urgent);font-size:.75rem">'
            f'{len(urgent_items)}</span></div>'
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
            inner += '<div class="empty-state" style="padding:.6rem 0 1.2rem">No urgent items.</div>'

        inner += (
            f'<div class="priority-group-label">'
            f'<span class="dot-i"></span> Important'
            f'<span style="margin-left:auto;color:var(--important);font-size:.75rem">'
            f'{len(important_items)}</span></div>'
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
            inner += '<div class="empty-state" style="padding:.6rem 0 1.2rem">No important items.</div>'

        if show_ignored:
            inner += (
                f'<div class="priority-group-label">'
                f'<span class="dot-g"></span> Low Priority'
                f'<span style="margin-left:auto;color:var(--ignore);font-size:.75rem">'
                f'{len(ignore_items)}</span></div>'
            )
            for item in ignore_items[:25]:
                inner += f'<div class="sent-card sent-ignore">{item["sentence"]}</div>'

        header_badges = (
            f'<span class="count-badge"><span class="dot-u"></span>{len(urgent_items)}</span>'
            f'<span class="count-badge"><span class="dot-i"></span>{len(important_items)}</span>'
        )
        if show_ignored:
            header_badges += f'<span class="count-badge"><span class="dot-g"></span>{len(ignore_items)}</span>'

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
