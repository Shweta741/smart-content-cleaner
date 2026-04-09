"""
main.py
AI Information Overload Filter — Streamlit entry point.
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
    page_title="AI Content Cleaner",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ---- Global ---- */
[data-testid="stAppViewContainer"] {
    background: #f7f8fc;
}
h1 { color: #1a1a2e; }
h2, h3 { color: #16213e; }

/* ---- Cards ---- */
.card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.card-urgent {
    border-left: 5px solid #e63946;
    background: #fff5f5;
}
.card-important {
    border-left: 5px solid #f4a261;
    background: #fffaf3;
}
.card-ignore {
    border-left: 5px solid #adb5bd;
    background: #f8f9fa;
}
.card-summary {
    border-left: 5px solid #457b9d;
    background: #f0f6ff;
}

/* ---- Badges ---- */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-left: 8px;
}
.badge-urgent    { background:#e63946; color:#fff; }
.badge-important { background:#f4a261; color:#fff; }
.badge-ignore    { background:#adb5bd; color:#fff; }

/* ---- Confidence bar ---- */
.conf-bar-wrap { background:#e9ecef; border-radius:6px; height:6px; margin-top:4px; }
.conf-bar      { height:6px; border-radius:6px; }

/* ---- Keyword pills ---- */
.pill {
    display: inline-block;
    background: #e8f4fd;
    color: #1d6fa4;
    border-radius: 20px;
    padding: 3px 12px;
    margin: 3px 3px;
    font-size: 0.82rem;
}
.pill-entity {
    background: #e8f8f0;
    color: #1a7a4a;
}

/* ---- Section divider ---- */
.section-divider {
    border: none;
    border-top: 1.5px solid #e2e8f0;
    margin: 1.6rem 0;
}

/* ---- Stat chips ---- */
.stat-chip {
    display: inline-block;
    background: #eef2ff;
    color: #4361ee;
    border-radius: 8px;
    padding: 4px 14px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-right: 8px;
}
</style>
""", unsafe_allow_html=True)


# ── Header ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 1.8rem 0 0.4rem 0;'>
    <h1 style='font-size:2.4rem; margin-bottom:0.2rem;'>🧹 AI Information Overload Filter</h1>
    <p style='color:#555; font-size:1.05rem; margin-top:0;'>
        Paste or upload any content — get a clean summary, key insights, and smart prioritization.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)


# ── Input section ───────────────────────────────────────────────────────────────
col_input, col_opts = st.columns([3, 1], gap="large")

with col_input:
    st.markdown("#### 📄 Input Content")

    input_mode = st.radio(
        "Choose input method:",
        ["✍️ Type / Paste Text", "📂 Upload File"],
        horizontal=True,
        label_visibility="collapsed",
    )

    raw_text = ""

    if input_mode == "✍️ Type / Paste Text":
        raw_text = st.text_area(
            "Enter your text here:",
            height=220,
            placeholder="Paste an email, article, report, meeting notes… anything.",
            label_visibility="visible",
        )
    else:
        uploaded = st.file_uploader(
            "Upload a .txt or .pdf file",
            type=["txt", "pdf"],
            label_visibility="collapsed",
        )
        if uploaded:
            if not validate_file_size(uploaded):
                st.error(f"⚠️ File exceeds {MAX_FILE_SIZE_MB} MB limit. Please upload a smaller file.")
            else:
                try:
                    if uploaded.name.endswith(".pdf"):
                        raw_text = read_pdf_file(uploaded)
                    else:
                        raw_text = read_txt_file(uploaded)
                    st.success(f"✅ File loaded: **{uploaded.name}** ({len(raw_text):,} characters)")
                except ValueError as e:
                    st.error(f"❌ {e}")

with col_opts:
    st.markdown("#### ⚙️ Options")
    summary_length = st.selectbox(
        "Summary length:",
        list(LENGTH_PRESETS.keys()),
        index=1,
    )
    show_ignored = st.checkbox("Show IGNORE sentences", value=False)

    st.markdown("<br>", unsafe_allow_html=True)
    process_btn = st.button("🚀 Process Content", use_container_width=True, type="primary")


# ── Processing ──────────────────────────────────────────────────────────────────
if process_btn:
    if not raw_text or not raw_text.strip():
        st.warning("⚠️ Please enter or upload some content first.")
        st.stop()

    # Truncate if needed
    text, was_truncated = truncate_text(raw_text)
    if was_truncated:
        st.info("ℹ️ Input was very long and has been trimmed to the first 15,000 characters for performance.")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # Pre-processing
    with st.spinner("🔍 Preprocessing text…"):
        prep = preprocess(text)

    if prep["language"] != "en":
        st.warning("⚠️ This content may not be in English. Results could be less accurate.")

    # Stats bar
    st.markdown(
        f"""
        <div style='margin-bottom:1rem;'>
            <span class='stat-chip'>📝 {prep['word_count']:,} words</span>
            <span class='stat-chip'>💬 {prep['sentence_count']} sentences</span>
            <span class='stat-chip'>🌐 Language: {prep['language'].upper()}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Three-column results layout ────────────────────────────────────────────
    col_left, col_right = st.columns([1.6, 1], gap="large")

    # ── LEFT: Summary ──────────────────────────────────────────────────────────
    with col_left:
        st.markdown("### 📋 Summary")
        with st.spinner("🤖 Generating summary (this may take ~30s on first run)…"):
            sum_result = summarize(prep["cleaned_text"], length=summary_length)

        if sum_result.get("error"):
            st.error(f"Summarization error: {sum_result['error']}")
        else:
            if sum_result.get("note"):
                st.info(f"ℹ️ {sum_result['note']}")
            st.markdown(
                f"<div class='card card-summary'>{sum_result['summary']}</div>",
                unsafe_allow_html=True,
            )

        # ── Key Insights ───────────────────────────────────────────────────────
        st.markdown("### 💡 Key Insights")
        insights = extract_key_insights(prep["sentences"], top_n=6)
        if insights:
            bullets = "".join(f"<li style='margin-bottom:6px;'>{s}</li>" for s in insights)
            st.markdown(
                f"<div class='card'><ul style='margin:0; padding-left:1.2rem;'>{bullets}</ul></div>",
                unsafe_allow_html=True,
            )
        else:
            st.info("No key insights could be extracted.")

        # ── Keywords ───────────────────────────────────────────────────────────
        st.markdown("### 🔑 Keywords & Entities")
        with st.spinner("Extracting keywords…"):
            kw = extract_keywords(prep["cleaned_text"])

        if kw.get("error"):
            st.warning(f"Keyword extraction unavailable: {kw['error']}")
        else:
            if kw["entities"]:
                pills = " ".join(f"<span class='pill pill-entity'>{e}</span>" for e in kw["entities"])
                st.markdown(
                    f"<div class='card'><strong>Named Entities</strong><br><br>{pills}</div>",
                    unsafe_allow_html=True,
                )
            if kw["noun_phrases"]:
                pills = " ".join(f"<span class='pill'>{p}</span>" for p in kw["noun_phrases"])
                st.markdown(
                    f"<div class='card'><strong>Key Phrases</strong><br><br>{pills}</div>",
                    unsafe_allow_html=True,
                )

    # ── RIGHT: Classified sentences ────────────────────────────────────────────
    with col_right:
        st.markdown("### 🗂️ Prioritized Sentences")
        with st.spinner("Classifying sentences…"):
            classified = classify_sentences(prep["sentences"])

        def _conf_bar(conf: float, color: str) -> str:
            pct = int(conf * 100)
            return (
                f"<div class='conf-bar-wrap'>"
                f"<div class='conf-bar' style='width:{pct}%; background:{color};'></div>"
                f"</div>"
            )

        # URGENT
        urgent_items = classified["URGENT"]
        with st.expander(f"🔴 URGENT  ({len(urgent_items)})", expanded=True):
            if urgent_items:
                for item in urgent_items:
                    st.markdown(
                        f"<div class='card card-urgent'>"
                        f"{item['sentence']}"
                        f"<div style='font-size:0.75rem;color:#888;margin-top:6px;'>"
                        f"Confidence {int(item['confidence']*100)}%"
                        f"</div>"
                        f"{_conf_bar(item['confidence'], '#e63946')}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown("<div class='card card-ignore'>No urgent items found.</div>", unsafe_allow_html=True)

        # IMPORTANT
        important_items = classified["IMPORTANT"]
        with st.expander(f"🟠 IMPORTANT  ({len(important_items)})", expanded=True):
            if important_items:
                for item in important_items:
                    st.markdown(
                        f"<div class='card card-important'>"
                        f"{item['sentence']}"
                        f"<div style='font-size:0.75rem;color:#888;margin-top:6px;'>"
                        f"Confidence {int(item['confidence']*100)}%"
                        f"</div>"
                        f"{_conf_bar(item['confidence'], '#f4a261')}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown("<div class='card card-ignore'>No important items found.</div>", unsafe_allow_html=True)

        # IGNORE
        if show_ignored:
            ignore_items = classified["IGNORE"]
            with st.expander(f"⚪ IGNORE  ({len(ignore_items)})", expanded=False):
                for item in ignore_items[:20]:   # cap display
                    st.markdown(
                        f"<div class='card card-ignore' style='font-size:0.88rem;color:#555;'>"
                        f"{item['sentence']}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )


# ── Footer ──────────────────────────────────────────────────────────────────────
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#aaa; font-size:0.82rem;'>"
    "AI Content Cleaner · Powered by 🤗 Transformers + spaCy + Streamlit"
    "</p>",
    unsafe_allow_html=True,
)
