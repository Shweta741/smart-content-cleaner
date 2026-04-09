"""
utils.py
Utility functions: keyword extraction with NLTK (no spaCy/blis dependency),
PDF reading, TXT reading, and file-size validation.
"""

import io
import re
import string
import streamlit as st
import nltk

# Download required NLTK data
nltk.download("averaged_perceptron_tagger_eng", quiet=True)
nltk.download("averaged_perceptron_tagger", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

MAX_FILE_SIZE_MB = 5
MAX_TEXT_CHARS   = 15_000

STOP_WORDS = set(stopwords.words("english"))
MEANINGFUL_TAGS = {"NN", "NNS", "NNP", "NNPS", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "JJ"}


def extract_keywords(text: str, top_n: int = 15) -> dict:
    """
    Extract keywords and named entities using NLTK POS tagging.
    Pure Python — no spaCy or blis required.
    """
    try:
        sample = text[:5000]
        tokens = word_tokenize(sample)
        tagged = nltk.pos_tag(tokens)

        # --- Named entities: consecutive proper nouns merged into phrases ---
        entities = []
        i = 0
        while i < len(tagged):
            word, tag = tagged[i]
            if tag in ("NNP", "NNPS") and word not in STOP_WORDS and len(word) > 1:
                phrase = [word]
                j = i + 1
                while j < len(tagged) and tagged[j][1] in ("NNP", "NNPS"):
                    phrase.append(tagged[j][0])
                    j += 1
                entities.append(" ".join(phrase))
                i = j
            else:
                i += 1

        seen = set()
        unique_entities = []
        for e in entities:
            key = e.lower()
            if key not in seen and len(e) > 1:
                seen.add(key)
                unique_entities.append(e)
        unique_entities = sorted(unique_entities)[:top_n]

        # --- Top keywords by frequency ---
        keywords = [
            word.lower()
            for word, tag in tagged
            if tag in MEANINGFUL_TAGS
            and word.lower() not in STOP_WORDS
            and word not in string.punctuation
            and len(word) > 2
            and word.isalpha()
        ]

        freq = {}
        for kw in keywords:
            freq[kw] = freq.get(kw, 0) + 1

        top_keywords = sorted(freq, key=freq.get, reverse=True)[:top_n]

        return {"entities": unique_entities, "noun_phrases": top_keywords, "error": None}

    except Exception as e:
        return {"entities": [], "noun_phrases": [], "error": str(e)}


def read_txt_file(uploaded_file) -> str:
    try:
        return uploaded_file.read().decode("utf-8", errors="replace")
    except Exception as e:
        raise ValueError(f"Could not read .txt file: {e}")


def read_pdf_file(uploaded_file) -> str:
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        pages = [page.extract_text() for page in reader.pages if page.extract_text()]
        if not pages:
            raise ValueError("No readable text found in PDF.")
        return "\n".join(pages)
    except ImportError:
        raise ValueError("PyPDF2 is not installed.")
    except Exception as e:
        raise ValueError(f"PDF read error: {e}")


def validate_file_size(uploaded_file) -> bool:
    uploaded_file.seek(0, 2)
    size_mb = uploaded_file.tell() / (1024 * 1024)
    uploaded_file.seek(0)
    return size_mb <= MAX_FILE_SIZE_MB


def truncate_text(text: str) -> tuple[str, bool]:
    if len(text) > MAX_TEXT_CHARS:
        return text[:MAX_TEXT_CHARS], True
    return text, False
