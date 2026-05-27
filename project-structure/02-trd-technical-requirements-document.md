# TRD — Technical Requirements Document

**The blueprint your AI agent needs to make technical decisions without guessing.**

---

## Frontend

- **Framework:** Simple HTML/JS (single page) or Next.js with TypeScript
- **Styling:** Tailwind CSS for rapid styling
- **Purpose:** Chat interface for user interactions

---

## Backend

- **Runtime:** Python with FastAPI
- **Purpose:** API endpoints for chat, image generation, moderation
- **Alternative:** Node.js with Express if preferred

---

## Database

- **Type:** SQLite (local) or PostgreSQL
- **Vector DB:** Chroma (local, open-source) for Bible verse embeddings
- **Purpose:** Scripture retrieval and grounding

---

## Auth

- **Method:** No authentication for v1 (public demo)
- **Future:** JWT tokens or session-based if user accounts needed

---

## Hosting

- **Frontend:** Vercel or Netlify (static hosting)
- **Backend:** Railway, Render, or local dev
- **Note:** Demo-focused, may run entirely locally

---

## Third-party APIs

| API | Purpose | Free/Paid |
|-----|---------|-----------|
| Claude API (Anthropic) | LLM for chat responses | Paid (free tier available) |
| OpenAI DALL-E 3 | Christian image generation | Paid (free tier available) |
| OpenAI Moderation API | Content safety filtering | Free |

---

## Key Libraries

- `fastapi` - Backend API framework
- `uvicorn` - ASGI server
- `anthropic` - Claude API client
- `openai` - DALL-E and Moderation API client
- `chromadb` - Vector database for RAG
- `sentence-transformers` - Text embeddings
- `python-dotenv` - Environment variable management

---

## Folder Structure

```
christian-ai-assistant/
├── docs/                    # Documentation
├── src/
│   ├── __init__.py
│   ├── main.py             # FastAPI entry point
│   ├── chat.py             # Chat endpoint logic RAG pipeline
│   ├── image_gen.py       # Image generation logic
│   ├── moderation.py       # Content moderation
│   ├── bible_db.py         # Bible verse database & retrieval
│   └── models.py           # Pydantic models
├── data/
│   └── kjv_bible.json      # Bible verse data
├── prompts/
│   └── system_prompts.py   # System prompt templates
├── tests/
│   ├── test_chat.py
│   ├── test_verse_detection.py
│   └── test_adversarial.py
├── static/
│   └── index.html         # Simple chat UI
├── .env.example           # Environment template
├── requirements.txt
└── README.md
```

---

## Environment Variables

```
ANTHROPIC_API_KEY=        # Claude API key
OPENAI_API_KEY=           # OpenAI API key (DALL-E + Moderation)
OPENAI_ORG=               # OpenAI organization (optional)
```

---

## Constraints

- Must work as a local demo without cloud deployment
- Must minimize API costs during development
- Must be completable within 5 hours using AI coding tools
- No mobile app in v1

---

*Part of SoluLab Project Documentation*
