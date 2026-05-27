"""
Initialize ChromaDB with Bible verse embeddings for RAG.
Run this script once to set up the vector database.
"""
import os
import json
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

#_dirs
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
BIBLE_JSON_PATH = os.path.join(DATA_DIR, "kjv_bible.json")

# Book name normalization (handle 1 Samuel -> 1 Samuel vs 1Samuel)
BOOK_DISPLAY_NAMES = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
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
    "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation"
]

def create_embedder():
    """Create a sentence transformer embedder."""
    print("Loading embedding model (this may take a minute)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return model

def init_chroma(embedder):
    """Initialize ChromaDB with Bible verses."""
    # Create client with persistent storage
    os.makedirs(CHROMA_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Get or create collection
    try:
        client.delete_collection("bible_verses")
    except Exception:
        pass

    collection = client.create_collection(
        name="bible_verses",
        metadata={"description": "KJV Bible verses for RAG grounding"}
    )

    # Load bible data
    with open(BIBLE_JSON_PATH, "r", encoding="utf-8") as f:
        verses = json.load(f)

    print(f"Processing {len(verses)} verses...")

    # Process in batches
    batch_size = 100
    for i in range(0, len(verses), batch_size):
        batch = verses[i:i+batch_size]
        texts = []
        ids = []
        metadatas = []

        for v in batch:
            # Format reference
            ref = f"{v['book']} {v['chapter']}:{v['verse']}"
            # Full text with reference
            text = f"{ref}: {v['text']}"
            verse_id = f"{v['book']}_{v['chapter']}_{v['verse']}"

            texts.append(text)
            ids.append(verse_id)
            metadatas.append({
                "book": v["book"],
                "chapter": v["chapter"],
                "verse": v["verse"],
                "reference": ref,
                "text": v["text"]
            })

        # Compute embeddings
        embeddings = embedder.encode(texts).tolist()

        # Add to collection
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

        print(f"  Processed {min(i+batch_size, len(verses))}/{len(verses)} verses")

    print(f"ChromaDB initialized with {collection.count()} verses")
    return collection


def main():
    embedder = create_embedder()
    collection = init_chroma(embedder)

    # Test query
    print("\n--- Test Query ---")
    results = collection.query(
        query_texts=["God love world"],
        n_results=3
    )
    print("Query 'God love world' results:")
    for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
        ref = metadata["reference"]
        text = metadata["text"][:80]
        print(f"  {ref}: {text}...")


if __name__ == "__main__":
    main()
