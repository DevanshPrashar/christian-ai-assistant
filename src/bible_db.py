"""
Bible database module for verse lookup and RAG grounding.
"""
import json
import os
from typing import Optional

# Use project root (one level up from src/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
BIBLE_JSON_PATH = os.path.join(DATA_DIR, "kjv_bible.json")

# Cache for bible data
_bible_cache: list[dict] | None = None


def get_bible_data() -> list[dict]:
    """Load and return the cached bible data."""
    global _bible_cache
    if _bible_cache is None:
        with open(BIBLE_JSON_PATH, "r", encoding="utf-8") as f:
            _bible_cache = json.load(f)
    return _bible_cache


def verse_exists(book: str, chapter: int, verse: int) -> bool:
    """Check if a specific verse exists in the Bible."""
    bible = get_bible_data()
    return any(
        v["book"].lower() == book.lower()
        and v["chapter"] == chapter
        and v["verse"] == verse
        for v in bible
    )


def get_verse(book: str, chapter: int, verse: int) -> Optional[dict]:
    """Get a specific verse by book, chapter, and verse number."""
    bible = get_bible_data()
    for v in bible:
        if (
            v["book"].lower() == book.lower()
            and v["chapter"] == chapter
            and v["verse"] == verse
        ):
            return v
    return None


def search_verses(query: str, limit: int = 5) -> list[dict]:
    """Search verses by text content (simple substring match)."""
    bible = get_bible_data()
    query_lower = query.lower()
    results = [v for v in bible if query_lower in v["text"].lower()]
    return results[:limit]


def get_verses_by_reference(reference: str) -> list[dict]:
    """
    Parse a reference like 'John 3:16' or 'John 3:16-18' and return matching verses.
    Returns empty list if reference cannot be parsed or verses not found.
    """
    reference = reference.strip()

    # Handle ranges like "John 3:16-18"
    if "-" in reference and ":" in reference:
        ref_part, range_part = reference.rsplit("-", 1)
        start_ref = ref_part.strip()
        end_verse = int(range_part.strip())
        # Parse start
        book_ch = start_ref.rsplit(" ", 1)
        if len(book_ch) != 2:
            return []
        book = book_ch[0].strip()
        ch_verse = book_ch[1].split(":")
        if len(ch_verse) != 2:
            return []
        chapter = int(ch_verse[0].strip())
        start_verse = int(ch_verse[1].strip())
        return get_verses_in_range(book, chapter, start_verse, end_verse)

    # Handle single verse
    parts = reference.rsplit(" ", 1)
    if len(parts) != 2:
        return []
    book = parts[0].strip()
    ch_verse = parts[1].split(":")
    if len(ch_verse) != 2:
        return []
    try:
        chapter = int(ch_verse[0].strip())
        verse = int(ch_verse[1].strip())
        v = get_verse(book, chapter, verse)
        return [v] if v else []
    except ValueError:
        return []


def get_verses_in_range(book: str, chapter: int, start_verse: int, end_verse: int) -> list[dict]:
    """Get a range of verses from the same chapter."""
    bible = get_bible_data()
    results = []
    for v in bible:
        if (
            v["book"].lower() == book.lower()
            and v["chapter"] == chapter
            and start_verse <= v["verse"] <= end_verse
        ):
            results.append(v)
    return sorted(results, key=lambda x: x["verse"])


def get_all_verses() -> list[dict]:
    """Return all verses from the Bible."""
    return get_bible_data()


def get_books() -> list[str]:
    """Return list of all Bible book names."""
    bible = get_bible_data()
    books = sorted(set(v["book"] for v in bible), key=lambda b: (
        ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
         "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
         "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah",
         "Esther", "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon",
         "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea",
         "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk",
         "Zephaniah", "Haggai", "Zechariah", "Malachi",
         "Matthew", "Mark", "Luke", "John", "Acts",
         "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
         "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
         "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
         "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation"].index(b)
        if b in ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
         "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
         "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah",
         "Esther", "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon",
         "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea",
         "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk",
         "Zephaniah", "Haggai", "Zechariah", "Malachi",
         "Matthew", "Mark", "Luke", "John", "Acts",
         "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
         "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
         "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
         "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation"]
        else 66
    ))
    return list(set(v["book"] for v in bible))


if __name__ == "__main__":
    # Test queries
    print("Testing John 3:16:", get_verse("John", 3, 16))
    print("Testing search 'love':", search_verses("love", limit=3))
    print("Total verses loaded:", len(get_all_verses()))
