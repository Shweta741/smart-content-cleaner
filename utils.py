"""
utils.py
Utility functions: keyword/entity extraction with spaCy,
PDF reading, and file-size validation.
"""

import io
import spacy
import streamlit as st

MAX_FILE_SIZE_MB = 5
MAX_TEXT_CHARS   = 15_000   # hard cap to keep inference fast


@st.cache_resource(show_spinner=False)
def load_spacy():
    """Load and cache the spaCy model."""
    try:
        nlp = spacy.load("en_core_web_sm")
        return nlp, None
    except Exception as e:
        return None, str(e)


def extract_keywords(text: str, top_n: int = 15) -> dict:
    """
    Extract named entities and important noun phrases using spaCy.

    Returns a dict with 'entities' and 'noun_phrases'.
    """
    nlp, err = load_spacy()
    if err:
        return {"entities": [], "noun_phrases": [], "error": err}

    doc = nlp(text[:5000])   # limit to avoid slow processing

    # Named entities (unique, sorted)
    entities = list({
        f"{ent.text} ({ent.label_})"
        for ent in doc.ents
        if ent.label_ not in ("CARDINAL", "ORDINAL", "QUANTITY")
    })
    entities = sorted(entities)[:top_n]

    # Noun chunks (unique, 2-5 words, non-trivial)
    noun_phrases = list({
        chunk.text.lower().strip()
        for chunk in doc.noun_chunks
        if 2 <= len(chunk.text.split()) <= 5
    })
    noun_phrases = sorted(noun_phrases, key=len, reverse=True)[:top_n]

    return {"entities": entities, "noun_phrases": noun_phrases, "error": None}


def read_txt_file(uploaded_file) -> str:
    """Read text from an uploaded .txt file."""
    try:
        content = uploaded_file.read()
        return content.decode("utf-8", errors="replace")
    except Exception as e:
        raise ValueError(f"Could not read .txt file: {e}")


def read_pdf_file(uploaded_file) -> str:
    """Extract text from an uploaded PDF using PyPDF2."""
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        if not pages:
            raise ValueError("No readable text found in PDF.")
        return "\n".join(pages)
    except ImportError:
        raise ValueError("PyPDF2 is not installed.")
    except Exception as e:
        raise ValueError(f"PDF read error: {e}")


def validate_file_size(uploaded_file) -> bool:
    """Return True if file is within the allowed size limit."""
    uploaded_file.seek(0, 2)        # seek to end
    size_mb = uploaded_file.tell() / (1024 * 1024)
    uploaded_file.seek(0)           # reset
    return size_mb <= MAX_FILE_SIZE_MB


def truncate_text(text: str) -> tuple[str, bool]:
    """
    Truncate text to MAX_TEXT_CHARS.
    Returns (truncated_text, was_truncated).
    """
    if len(text) > MAX_TEXT_CHARS:
        return text[:MAX_TEXT_CHARS], True
    return text, False
