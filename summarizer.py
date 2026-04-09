"""
summarizer.py
AI summarization using sshleifer/distilbart-cnn-12-6.
Calls model.generate() directly — no pipeline() task registry needed.
Fully compatible with newer transformers versions on Streamlit Cloud.
"""

import torch
import streamlit as st
from transformers import BartTokenizer, BartForConditionalGeneration

MODEL_NAME = "sshleifer/distilbart-cnn-12-6"

# Summary length presets: (min_new_tokens, max_new_tokens)
LENGTH_PRESETS = {
    "Short":  (30,  80),
    "Medium": (60,  150),
    "Long":   (100, 250),
}

MAX_INPUT_TOKENS      = 1024   # model hard limit
MAX_CHUNK_WORDS       = 700    # safe word count per chunk
MIN_WORDS_FOR_SUMMARY = 30


@st.cache_resource(show_spinner=False)
def load_model():
    """
    Load and cache tokenizer + model directly.
    Avoids pipeline() task-registry entirely — works on any transformers version.
    """
    try:
        tokenizer = BartTokenizer.from_pretrained(MODEL_NAME)
        model     = BartForConditionalGeneration.from_pretrained(MODEL_NAME)
        model.eval()   # inference mode
        return tokenizer, model, None
    except Exception as e:
        return None, None, str(e)


def _summarize_chunk(
    text: str,
    tokenizer,
    model,
    min_len: int,
    max_len: int,
) -> str:
    """Summarize a single chunk of text using model.generate()."""
    inputs = tokenizer(
        text,
        return_tensors="pt",
        max_length=MAX_INPUT_TOKENS,
        truncation=True,
    )
    with torch.no_grad():
        summary_ids = model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            num_beams=4,
            min_length=min_len,
            max_length=max_len,
            early_stopping=True,
            no_repeat_ngram_size=3,
        )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True).strip()


def _chunk_text(text: str, max_words: int = MAX_CHUNK_WORDS) -> list[str]:
    """Split long text into manageable word-count chunks."""
    words = text.split()
    return [
        " ".join(words[i : i + max_words])
        for i in range(0, len(words), max_words)
    ]


def summarize(text: str, length: str = "Medium") -> dict:
    """
    Generate a summary for the given text.

    Args:
        text:   Cleaned input text.
        length: 'Short', 'Medium', or 'Long'.

    Returns:
        dict with keys 'summary' (str), 'note' (str|None), 'error' (str|None).
    """
    word_count = len(text.split())

    if word_count < MIN_WORDS_FOR_SUMMARY:
        return {
            "summary": text,
            "note": "Text too short for summarization — showing original.",
            "error": None,
        }

    tokenizer, model, load_error = load_model()
    if load_error:
        return {"summary": "", "note": None, "error": f"Model load error: {load_error}"}

    min_len, max_len = LENGTH_PRESETS.get(length, LENGTH_PRESETS["Medium"])

    try:
        chunks = _chunk_text(text)
        partial_summaries = []

        for chunk in chunks:
            chunk_words = len(chunk.split())
            # Scale length limits to chunk size
            c_max = min(max_len, max(20, chunk_words // 2))
            c_min = min(min_len, max(10, c_max - 20))
            summary = _summarize_chunk(chunk, tokenizer, model, c_min, c_max)
            partial_summaries.append(summary)

        final_summary = " ".join(partial_summaries)

        # Second-pass merge if still too long
        if len(partial_summaries) > 1 and len(final_summary.split()) > max_len:
            final_summary = _summarize_chunk(
                final_summary, tokenizer, model, min_len, max_len
            )

        return {"summary": final_summary, "note": None, "error": None}

    except Exception as e:
        return {"summary": "", "note": None, "error": str(e)}
