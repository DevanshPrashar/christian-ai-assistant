"""
Simplified RAG retrieval using Bible DB.
No external embedding models required - uses keyword matching.
For production, can upgrade to ChromaDB with sentence-transformers.
"""
import os
from typing import List, Dict
from src.bible_db import get_bible_data, search_verses

# Cache for search index
_search_index: List[Dict] | None = None


def get_search_index() -> List[Dict]:
    """Get or create the search index."""
    global _search_index
    if _search_index is None:
        _search_index = get_bible_data()
    return _search_index


def retrieve_relevant_verses(query: str, limit: int = 5) -> List[Dict]:
    """
    Retrieve verses relevant to a query using simple text matching.
    Returns verses with their book, chapter, verse, and text.
    """
    if not query or not query.strip():
        return []

    results = search_verses(query, limit=limit)

    # Format results
    formatted = []
    for v in results:
        formatted.append({
            "book": v["book"],
            "chapter": v["chapter"],
            "verse": v["verse"],
            "reference": f"{v['book']} {v['chapter']}:{v['verse']}",
            "text": v["text"]
        })
    return formatted


def format_verse_for_context(verse: dict) -> str:
    """Format a verse for injection into the prompt context."""
    ref = verse["reference"]
    text = verse["text"]
    return f"[{ref}] {text}"


def build_context_for_query(query: str, max_verses: int = 5) -> str:
    """
    Build a context string with relevant Bible verses for a query.
    Used to inject scripture grounding into prompts.
    """
    verses = retrieve_relevant_verses(query, limit=max_verses)
    if not verses:
        return ""

    context_parts = ["Here are relevant Bible verses that may help answer this question:"]
    for v in verses:
        context_parts.append(format_verse_for_context(v))

    return "\n".join(context_parts)


if __name__ == "__main__":
    # Test
    query = "What does the Bible say about love?"
    context = build_context_for_query(query)
    print(f"Query: {query}")
    print(f"\nContext:\n{context}")
