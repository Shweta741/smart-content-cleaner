"""
summarizer.py
AI summarization using HuggingFace distilbart-cnn-12-6.
Loads model/tokenizer explicitly to avoid task-registry issues
in newer transformers versions.
"""

import streamlit as st
from transformers import BartTokenizer, BartForConditionalGeneration, pipeline

MODEL_NAME = "sshleifer/distilbart-cnn-12-6"

# Length presets: (min_length, max_length)
LENGTH_PRESETS = {
    "Short":  (30,  80),
    "Medium": (60,  150),
    "Long":   (100, 250),
}

MAX_CHUNK_WORDS   = 900
MIN_WORDS_FOR_SUMMARY = 30


@st.cache_resource(show_spinner=False)
def load_summarizer():
    """
    Load tokenizer and model explicitly, then wrap in a pipeline.
    Avoids 'Unknown task summarization' error in newer transformers.
    """
    try:
        tokenizer = BartTokenizer.from_pretrained(MODEL_NAME)
        model     = BartForConditionalGeneration.from_pretrained(MODEL_NAME)
        summarizer = pipeline(
            "summarization",
            model=model,
            tokenizer=tokenizer,
            framework="pt",
            device=-1,       # CPU only — safe for Streamlit Cloud
        )
        return summarizer, None
    except Exception as e:
        return None, str(e)


def _chunk_text(text: str, max_words: int = MAX_CHUNK_WORDS) -> list[str]:
    """Split long text into word-based chunks the model can handle."""
    words = text.split()
    return [
        " ".join(words[i : i + max_words])
        for i in range(0, len(words), max_words)
    ]


def summarize(text: str, length: str = "Medium") -> dict:
    """
    Generate a summary for the provided text.

    Args:
        text:   Cleaned input text.
        length: One of 'Short', 'Medium', 'Long'.

    Returns:
        dict with 'summary' (str), optional 'note' (str), and 'error' (str|None).
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

        # Second-pass merge if multi-chunk result is still too long
        if len(partial_summaries) > 1 and len(final_summary.split()) > max_len:
            result = summarizer(
                final_summary,
                max_length=max_len,
                min_length=min_len,
                do_sample=False,
            )
            final_summary = result[0]["summary_text"]

        return {"summary": final_summary.strip(), "note": None, "error": None}

    except Exception as e:
        return {"summary": "", "note": None, "error": str(e)}
