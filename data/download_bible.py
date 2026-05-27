"""
Download all KJV Bible books from aruljohn/Bible-kjv GitHub repo
and merge into a single kjv_bible.json file.
"""
import json
import requests
import os

BASE_URL = "https://raw.githubusercontent.com/aruljohn/Bible-kjv/master"

BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1Samuel", "2Samuel",
    "1Kings", "2Kings", "1Chronicles", "2Chronicles", "Ezra", "Nehemiah",
    "Esther", "Job", "Psalms", "Proverbs", "Ecclesiastes", "SongofSolomon",
    "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea",
    "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk",
    "Zephaniah", "Haggai", "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "1Corinthians", "2Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1Thessalonians", "2Thessalonians",
    "1Timothy", "2Timothy", "Titus", "Philemon", "Hebrews", "James",
    "1Peter", "2Peter", "1John", "2John", "3John", "Jude", "Revelation"
]

def download_bible():
    all_verses = []

    for book in BOOKS:
        print(f"Downloading {book}...")
        url = f"{BASE_URL}/{book}.json"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"  Failed to download {book}")
            continue

        data = response.json()
        book_name = data.get("book", book)

        for chapter_data in data.get("chapters", []):
            chapter = chapter_data.get("chapter")
            for verse_data in chapter_data.get("verses", []):
                verse = verse_data.get("verse")
                text = verse_data.get("text")
                if text:
                    all_verses.append({
                        "book": book_name,
                        "chapter": int(chapter) if chapter else 0,
                        "verse": int(verse) if verse else 0,
                        "text": text
                    })

    print(f"\nTotal verses downloaded: {len(all_verses)}")

    output_path = os.path.join(os.path.dirname(__file__), "kjv_bible.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_verses, f, indent=2)

    print(f"Saved to {output_path}")
    return all_verses

if __name__ == "__main__":
    download_bible()
