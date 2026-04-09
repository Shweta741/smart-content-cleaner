"""
summarizer.py
AI summarization using HuggingFace distilbart-cnn-12-6.
Handles chunking for long texts and summary length control.
"""

import streamlit as st
from transformers import pipeline

MODEL_NAME = "sshleifer/distilbart-cnn-12-6"

# Length presets: (min_length, max_length)
LENGTH_PRESETS = {
    "Short":  (30,  80),
    "Medium": (60,  150),
    "Long":   (100, 250),
}

# Max tokens the model can handle per chunk
MAX_CHUNK_TOKENS = 900   # conservative limit (model max is ~1024)
MIN_WORDS_FOR_SUMMARY = 30


@st.cache_resource(show_spinner=False)
def load_summarizer():
    """Load and cache the summarization pipeline."""
    try:
        summarizer = pipeline(
            "summarization",
            model=MODEL_NAME,
            device=-1,          # CPU only — safe for cloud
        )
        return summarizer, None
    except Exception as e:
        return None, str(e)


def _chunk_text(text: str, max_words: int = MAX_CHUNK_TOKENS) -> list[str]:
    """Split long text into word-based chunks the model can handle."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i : i + max_words])
        chunks.append(chunk)
    return chunks


def summarize(text: str, length: str = "Medium") -> dict:
    """
    Generate a summary for the provided text.

    Args:
        text:   Cleaned input text.
        length: One of 'Short', 'Medium', 'Long'.

    Returns:
        dict with 'summary' (str) and optional 'error' (str).
    """
    word_count = len(text.split())

    if word_count < MIN_WORDS_FOR_SUMMARY:
        return {
            "summary": text,
            "note": "Text too short for summarization — showing original.",
            "error": None,
        }

    summarizer, load_error = load_summarizer()
    if load_error:
        return {"summary": "", "error": f"Model load error: {load_error}"}

    min_len, max_len = LENGTH_PRESETS.get(length, LENGTH_PRESETS["Medium"])

    try:
        chunks = _chunk_text(text)
        partial_summaries = []

        for chunk in chunks:
            chunk_words = len(chunk.split())
            # Adjust lengths relative to chunk size
            c_max = min(max_len, max(20, chunk_words // 2))
            c_min = min(min_len, c_max - 10)

            result = summarizer(
                chunk,
                max_length=c_max,
                min_length=c_min,
                do_sample=False,
            )
            partial_summaries.append(result[0]["summary_text"])

        final_summary = " ".join(partial_summaries)

        # If we have multiple chunk summaries, do a second-pass summary
        if len(partial_summaries) > 1 and len(final_summary.split()) > max_len:
            result = summarizer(
                final_summary,
                max_length=max_len,
                min_length=min_len,
                do_sample=False,
            )
            final_summary = result[0]["summary_text"]

        return {"summary": final_summary.strip(), "error": None}

    except Exception as e:
        return {"summary": "", "error": str(e)}
