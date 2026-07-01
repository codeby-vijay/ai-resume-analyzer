"""Text cleaning and NLP preprocessing pipeline.

Steps implemented: lowercase, punctuation removal, stopword removal,
lemmatization. spaCy's small English model is used for tokenization and
lemmatization; it is loaded lazily and cached at module level so it is
only loaded once per worker process.
"""
import re
import string
from functools import lru_cache

_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "so", "of", "at",
    "by", "for", "with", "about", "against", "between", "into", "through",
    "during", "before", "after", "above", "below", "to", "from", "up",
    "down", "in", "out", "on", "off", "over", "under", "again", "further",
    "once", "here", "there", "when", "where", "why", "how", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "than", "too", "very", "s", "t",
    "can", "will", "just", "don", "should", "now", "is", "are", "was",
    "were", "be", "been", "being", "have", "has", "had", "having", "do",
    "does", "did", "doing", "i", "me", "my", "myself", "we", "our", "ours",
    "you", "your", "he", "him", "his", "she", "her", "it", "its", "they",
    "them", "their", "this", "that", "these", "those",
}


@lru_cache(maxsize=1)
def _get_spacy_model():
    try:
        import spacy
        try:
            return spacy.load("en_core_web_sm")
        except OSError:
            # Model not downloaded; fall back to a blank English pipeline
            # with a lemmatizer disabled (rule-based lemmatizer unavailable
            # without the model data, so we degrade gracefully).
            return spacy.blank("en")
    except ImportError:
        return None


def clean_text(text: str) -> str:
    """Lowercase, strip punctuation/extra whitespace."""
    text = text.lower()
    text = re.sub(r"[^\w\s\+\#\./-]", " ", text)  # keep tokens like c++, c#, node.js
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def remove_stopwords(text: str) -> str:
    tokens = text.split()
    return " ".join(t for t in tokens if t not in _STOPWORDS)


def lemmatize(text: str) -> str:
    nlp = _get_spacy_model()
    if nlp is None:
        return text
    doc = nlp(text)
    if doc.has_annotation("LEMMA") if hasattr(doc, "has_annotation") else False:
        return " ".join(tok.lemma_ for tok in doc)
    # blank pipeline without lemmatizer -> return tokenized text unchanged
    return " ".join(tok.text for tok in doc) if len(doc) else text


def preprocess(text: str) -> str:
    """Full pipeline: lowercase -> remove punctuation -> remove stopwords -> lemmatize."""
    cleaned = clean_text(text)
    no_stop = remove_stopwords(cleaned)
    lemmatized = lemmatize(no_stop)
    return lemmatized
