"""
Verse validation module for detecting fake or hallucinated scripture.
Verifies Bible verse references against the KJV database.
"""
import re
from typing import Optional

from src.bible_db import verse_exists, get_verse, get_verses_by_reference


class VerseValidationResult:
    """Result of verse validation."""
    def __init__(self, is_valid: bool, reference: str, verified_text: Optional[str] = None,
                 error_message: Optional[str] = None, is_fake: bool = False):
        self.is_valid = is_valid
        self.reference = reference
        self.verified_text = verified_text
        self.error_message = error_message
        self.is_fake = is_fake

    def __repr__(self):
        return f"VerseValidationResult(valid={self.is_valid}, ref={self.reference}, fake={self.is_fake})"


def parse_bible_reference(text: str) -> list[tuple[str, int, int]]:
    """
    Parse text for Bible references in various formats.
    Returns list of (book, chapter, verse) tuples found.
    """
    # Pattern for book name followed by chapter:verse
    # Handles: John 3:16, 1 John 3:16, Genesis 1:1, 2 Samuel 5:1
    pattern = r'\b([1-3]?\s*[A-Za-z]+)\s+(\d+):(\d+)'

    matches = []
    found = re.findall(pattern, text)
    for match in found:
        book = match[0].strip()
        try:
            chapter = int(match[1])
            verse = int(match[2])
            # Normalize book name
            book = normalize_book_name(book)
            if book:
                matches.append((book, chapter, verse))
        except ValueError:
            continue

    return matches


def normalize_book_name(book: str) -> Optional[str]:
    """
    Normalize book name to standard KJV format.
    Returns None if book is not recognized.
    """
    book_map = {
        "genesis": "Genesis", "exodus": "Exodus", "leviticus": "Leviticus",
        "numbers": "Numbers", "deuteronomy": "Deuteronomy", "joshua": "Joshua",
        "judges": "Judges", "ruth": "Ruth", "1 samuel": "1 Samuel",
        "2 samuel": "2 Samuel", "1 kings": "1 Kings", "2 kings": "2 Kings",
        "1 chronicles": "1 Chronicles", "2 chronicles": "2 Chronicles",
        "ezra": "Ezra", "nehemiah": "Nehemiah", "esther": "Esther", "job": "Job",
        "psalms": "Psalms", "psalm": "Psalms", "proverbs": "Proverbs",
        "ecclesiastes": "Ecclesiastes", "song of solomon": "Song of Solomon",
        "isaiah": "Isaiah", "jeremiah": "Jeremiah", "lamentations": "Lamentations",
        "ezeaniel": "Ezekiel", "daniel": "Daniel", "hosea": "Hosea", "joel": "Joel",
        "amos": "Amos", "obadiah": "Obadiah", "jonah": "Jonah", "micah": "Micah",
        "nahum": "Nahum", "habakkuk": "Habakkuk", "zephaniah": "Zephaniah",
        "haggai": "Haggai", "zechariah": "Zechariah", "malachi": "Malachi",
        "matthew": "Matthew", "mark": "Mark", "luke": "Luke", "john": "John",
        "acts": "Acts", "romans": "Romans", "1 corinthians": "1 Corinthians",
        "2 corinthians": "2 Corinthians", "galatians": "Galatians",
        "ephesians": "Ephesians", "philippians": "Philippians",
        "colossians": "Colossians", "1 thessalonians": "1 Thessalonians",
        "2 thessalonians": "2 Thessalonians", "1 timothy": "1 Timothy",
        "2 timothy": "2 Timothy", "titus": "Titus", "philemon": "Philemon",
        "hebrews": "Hebrews", "james": "James", "1 peter": "1 Peter",
        "2 peter": "2 Peter", "1 john": "1 John", "2 john": "2 John",
        "3 john": "3 John", "jude": "Jude", "revelation": "Revelation",
        # Common misspellings/variants
        "song of songs": "Song of Solomon", "songs": "Song of Solomon",
        "ezekiel": "Ezekiel", "dan": "Daniel", "rev": "Revelation",
        "ge": "Genesis", "ex": "Exodus", "le": "Leviticus", "nu": "Numbers",
        "dt": "Deuteronomy", "jos": "Joshua", "jg": "Judges", "ru": "Ruth",
        "1 sa": "1 Samuel", "2 sa": "2 Samuel", "1 ki": "1 Kings", "2 ki": "2 Kings",
        "1 ch": "1 Chronicles", "2 ch": "2 Chronicles", "ez": "Ezra", "ne": "Nehemiah",
        "est": "Esther", "job": "Job", "ps": "Psalms", "pr": "Proverbs",
        "ec": "Ecclesiastes", "so": "Song of Solomon", "isa": "Isaiah",
        "jer": "Jeremiah", "la": "Lamentations", "eze": "Ezekiel", "da": "Daniel",
        "ho": "Hosea", "jl": "Joel", "am": "Amos", "ob": "Obadiah", "jon": "Jonah",
        "mic": "Micah", "na": "Nahum", "hab": "Habakkuk", "zep": "Zephaniah",
        "hag": "Haggai", "zec": "Zechariah", "mal": "Malachi", "mt": "Matthew",
        "mk": "Mark", "lk": "Luke", "jn": "John", "ac": "Acts", "rm": "Romans",
        "1 co": "1 Corinthians", "2 co": "2 Corinthians", "ga": "Galatians",
        "eph": "Ephesians", "php": "Philippians", "col": "Colossians",
        "1 th": "1 Thessalonians", "2 th": "2 Thessalonians", "1 ti": "1 Timothy",
        "2 ti": "2 Timothy", "tit": "Titus", "phm": "Philemon", "heb": "Hebrews",
        "jas": "James", "1 pe": "1 Peter", "2 pe": "2 Peter", "1 jn": "1 John",
        "2 jn": "2 John", "3 jn": "3 John", "jud": "Jude", "rev": "Revelation",
    }

    book_lower = book.lower().strip()
    return book_map.get(book_lower)


def validate_verse(book: str, chapter: int, verse: int) -> VerseValidationResult:
    """
    Validate a single verse exists in the KJV Bible.
    """
    # Normalize book name
    normalized_book = normalize_book_name(book)
    if not normalized_book:
        return VerseValidationResult(
            is_valid=False,
            reference=f"{book} {chapter}:{verse}",
            error_message=f"Unknown book: {book}",
            is_fake=True
        )

    # Check if verse exists
    if verse_exists(normalized_book, chapter, verse):
        verse_data = get_verse(normalized_book, chapter, verse)
        return VerseValidationResult(
            is_valid=True,
            reference=f"{normalized_book} {chapter}:{verse}",
            verified_text=verse_data["text"] if verse_data else None
        )
    else:
        return VerseValidationResult(
            is_valid=False,
            reference=f"{normalized_book} {chapter}:{verse}",
            error_message=f"Verse {chapter}:{verse} not found in {normalized_book}",
            is_fake=True
        )


def validate_verse_reference(reference: str) -> VerseValidationResult:
    """
    Validate a full verse reference like "John 3:16".
    """
    verses = get_verses_by_reference(reference)
    if verses:
        v = verses[0]
        return VerseValidationResult(
            is_valid=True,
            reference=reference,
            verified_text=v["text"]
        )
    else:
        # Try to parse and provide helpful error
        parts = reference.strip().rsplit(" ", 1)
        if len(parts) == 2:
            book_part = parts[0]
            ch_verse = parts[1].split(":")
            if len(ch_verse) == 2:
                try:
                    chapter = int(ch_verse[0])
                    verse = int(ch_verse[1])
                    normalized = normalize_book_name(book_part)
                    if normalized:
                        return VerseValidationResult(
                            is_valid=False,
                            reference=reference,
                            error_message=f"{normalized} {chapter}:{verse} is not a valid verse",
                            is_fake=True
                        )
                    else:
                        return VerseValidationResult(
                            is_valid=False,
                            reference=reference,
                            error_message=f"Unknown book: {book_part}",
                            is_fake=True
                        )
                except ValueError:
                    pass

        return VerseValidationResult(
            is_valid=False,
            reference=reference,
            error_message=f"Could not parse verse reference: {reference}",
            is_fake=True
        )


def validate_response_verses(text: str) -> list[VerseValidationResult]:
    """
    Extract and validate all verse references from a response.
    Returns list of validation results for each found reference.
    """
    parsed_refs = parse_bible_reference(text)
    results = []

    for book, chapter, verse in parsed_refs:
        result = validate_verse(book, chapter, verse)
        results.append(result)

    return results


def get_fake_verses(text: str) -> list[VerseValidationResult]:
    """
    Get only the fake/unverified verses from a text.
    """
    all_validations = validate_response_verses(text)
    return [r for r in all_validations if not r.is_valid]


def format_verse_warning(fake_verses: list[VerseValidationResult]) -> str:
    """
    Format a warning message for fake verses found in a response.
    """
    if not fake_verses:
        return ""

    warnings = []
    for verse in fake_verses:
        if verse.error_message:
            warnings.append(f"- {verse.reference}: {verse.error_message}")
        else:
            warnings.append(f"- {verse.reference}: Could not verify this reference")

    return "⚠️ **Verse Verification Warning**\n\nThe following scripture references could not be verified:\n" + "\n".join(warnings) + "\n\nPlease verify these references independently."


# Test if run directly
if __name__ == "__main__":
    test_refs = [
        "John 3:16",  # Valid
        "Exodus 20:14",  # Valid (Commandment)
        "Genesis 1:1",  # Valid
        "John 10:34",  # Valid
        "Matthew 7:12",  # Valid
        # Potentially fake/varied
        "Proverbs 3:5",  # Valid
        "James 1:5",  # Valid
    ]

    print("Testing verse validation...\n")
    for ref in test_refs:
        result = validate_verse_reference(ref)
        status = "✓" if result.is_valid else "✗"
        print(f"{status} {ref}: {result.verified_text[:50]}... ({result.error_message or 'OK'})")