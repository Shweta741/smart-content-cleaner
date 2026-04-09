"""
preprocessing.py
Handles text cleaning, tokenization, deduplication, and language detection.
"""

import re
import nltk
from nltk.tokenize import sent_tokenize

# Download required NLTK data
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)


def clean_text(text: str) -> str:
    """Remove extra whitespace and unwanted special characters."""
    # Replace multiple newlines/spaces with single space
    text = re.sub(r"\s+", " ", text)
    # Remove non-ASCII characters except basic punctuation
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    # Remove repeated punctuation
    text = re.sub(r"([!?.]){2,}", r"\1", text)
    return text.strip()


def tokenize_sentences(text: str) -> list[str]:
    """Split text into individual sentences using NLTK."""
    sentences = sent_tokenize(text)
    # Filter out very short sentences (noise)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    return sentences


def remove_duplicates(sentences: list[str]) -> list[str]:
    """Remove duplicate or near-duplicate sentences (case-insensitive)."""
    seen = set()
    unique = []
    for s in sentences:
        normalized = s.lower().strip()
        if normalized not in seen:
            seen.add(normalized)
            unique.append(s)
    return unique


def detect_language(text: str) -> str:
    """
    Simple heuristic language detection.
    Returns 'en' if English-looking, else 'unknown'.
    """
    try:
        # Count common English function words
        english_markers = [
            " the ", " is ", " are ", " was ", " were ",
            " and ", " that ", " this ", " with ", " for ",
            " have ", " has ", " been ", " will ", " can ",
        ]
        sample = " " + text[:500].lower() + " "
        hits = sum(1 for w in english_markers if w in sample)
        return "en" if hits >= 3 else "unknown"
    except Exception:
        return "unknown"


def preprocess(text: str) -> dict:
    """
    Full preprocessing pipeline.
    Returns a dict with cleaned text, sentences, and language.
    """
    cleaned = clean_text(text)
    sentences = tokenize_sentences(cleaned)
    sentences = remove_duplicates(sentences)
    language = detect_language(cleaned)

    return {
        "cleaned_text": cleaned,
        "sentences": sentences,
        "language": language,
        "sentence_count": len(sentences),
        "word_count": len(cleaned.split()),
    }
