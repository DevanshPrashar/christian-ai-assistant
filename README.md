# Christian AI Assistant

A faithful AI companion for Christians — answering questions, generating content, and staying grounded in Biblical truth.

## Features

- **Scripture-Aware Responses** — Answers grounded in verifiable Bible verses
- **Christian Image Generation** — Create Biblically-themed images with safety moderation
- **Conversation Memory** — Context-aware responses across multiple exchanges
- **Denomination-Aware** — Respectful of Catholic, Protestant, Orthodox, and other traditions
- **Safety Layer** — Blocks offensive/heretical content and detects fake scripture

## Tech Stack

- **Backend:** Python + FastAPI
- **LLM:** Claude API (Anthropic)
- **Image Gen:** DALL-E 3 (OpenAI)
- **Vector DB:** ChromaDB for scripture embeddings
- **Moderation:** OpenAI Moderation API

## Setup

1. **Clone the repo**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure API keys:**
   ```bash
   cp .env.example .env
   # Add your API keys to .env
   ```
4. **Initialize the Bible database:**
   ```bash
   python -m src.bible_db
   ```
5. **Run the server:**
   ```bash
   uvicorn src.main:app --reload
   ```
6. **Open** `static/index.html` **in your browser**

## Project Structure

```
├── src/
│   ├── main.py          # FastAPI entry point
│   ├── chat.py          # Chat endpoint with RAG pipeline
│   ├── image_gen.py     # Image generation
│   ├── moderation.py    # Content moderation
│   ├── bible_db.py      # Bible verse database
│   └── models.py        # Pydantic models
├── data/
│   └── kjv_bible.json   # Bible verse data
├── prompts/
│   └── system_prompts.py # System prompt templates
├── static/
│   └── index.html       # Chat UI
├── docs/                # SoluLab documentation
├── project-structure/   # Formal documentation
├── requirements.txt
└── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Send a message and receive a grounded response |
| `/generate-image` | POST | Generate a Christian-themed image |
| `/health` | GET | Health check |

## Safety Features

- Input/output content moderation
- Fake Bible verse detection
- Adversarial prompt handling
- Graceful denial for policy-violating requests

## License

MIT
