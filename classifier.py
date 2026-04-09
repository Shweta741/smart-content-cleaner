"""
classifier.py
Rule-based sentence classifier: URGENT / IMPORTANT / IGNORE.
Assigns a confidence score to each sentence.
"""

URGENT_KEYWORDS = [
    "urgent", "asap", "immediately", "deadline", "tomorrow",
    "priority", "critical", "overdue", "right away", "now",
]

IMPORTANT_KEYWORDS = [
    "meeting", "decision", "action", "plan", "update", "submit",
    "review", "approve", "confirm", "required", "must", "need",
    "report", "schedule", "agenda", "discuss", "follow up",
]


def _score_sentence(sentence: str) -> dict:
    """
    Score a sentence and classify it.

    Confidence is calculated as a simple ratio of keyword hits
    to the total keyword pool, scaled to [0.0, 1.0].
    """
    lower = sentence.lower()

    urgent_hits   = sum(1 for kw in URGENT_KEYWORDS    if kw in lower)
    important_hits = sum(1 for kw in IMPORTANT_KEYWORDS if kw in lower)

    if urgent_hits > 0:
        label = "URGENT"
        # More keyword hits → higher confidence
        confidence = min(0.95, 0.60 + urgent_hits * 0.12)
    elif important_hits > 0:
        label = "IMPORTANT"
        confidence = min(0.90, 0.50 + important_hits * 0.10)
    else:
        label = "IGNORE"
        confidence = 0.85   # high confidence it's noise

    return {
        "sentence": sentence,
        "label": label,
        "confidence": round(confidence, 2),
        "urgent_hits": urgent_hits,
        "important_hits": important_hits,
    }


def classify_sentences(sentences: list[str]) -> dict:
    """
    Classify a list of sentences.

    Returns a dict keyed by label containing lists of scored sentences.
    """
    results = {"URGENT": [], "IMPORTANT": [], "IGNORE": []}

    for sentence in sentences:
        scored = _score_sentence(sentence)
        results[scored["label"]].append(scored)

    return results


def extract_key_insights(sentences: list[str], top_n: int = 5) -> list[str]:
    """
    Return the top_n most 'important' or 'urgent' sentences
    as key insights, sorted by confidence.
    """
    scored = [_score_sentence(s) for s in sentences]
    # Keep only non-IGNORE with highest confidence
    noteworthy = [s for s in scored if s["label"] != "IGNORE"]
    noteworthy.sort(key=lambda x: x["confidence"], reverse=True)

    # Fall back to top sentences by position if nothing urgent/important
    if not noteworthy:
        return sentences[:top_n]

    return [item["sentence"] for item in noteworthy[:top_n]]
