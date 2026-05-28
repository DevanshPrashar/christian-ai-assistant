# Architecture Diagram

```mermaid
graph TB
    subgraph Client["🌐 Client Layer"]
        Browser[("Browser<br/>static/index.html")]
    end

    subgraph Vercel["☁️ Vercel Cloud"]
        subgraph API["Python Serverless (FastAPI)"]
            Static[("Static Files<br/>/")]
            ChatEP[("Chat Endpoint<br/>/chat")]
            ImageEP[("Image Endpoint<br/>/generate-image")]
            HealthEP[("Health Endpoint<br/>/health")]
        end

        subgraph Core["⚙️ Core Modules"]
            Moderation["Moderation Layer<br/>moderation.py"]
            ChatProc["Chat Processor<br/>chat.py"]
            ImageGen["Image Generator<br/>image_gen.py"]
            Tricky["Tricky Scenarios<br/>tricky_scenarios.py"]
            VerseVal["Verse Validator<br/>verse_validator.py"]
        end

        subgraph External["🔗 External APIs"]
            MiniMax["MiniMax API<br/>MiniMax-M2.7"]
            MiniMaxImg["MiniMax Image<br/>image-01"]
            OpenAI["OpenAI API<br/>Moderation"]
        end

        subgraph Data["📦 Data Layer"]
            BibleDB[("Bible DB<br/>kjv_bible.json")]
            ChromaDB[("In-Memory<br/>Conversation Cache")]
        end
    end

    %% Connections
    Browser --> Static
    Browser --> ChatEP
    Browser --> ImageEP

    ChatEP --> Moderation
    ChatEP --> Tricky
    ChatEP --> ChatProc
    ChatEP --> VerseVal

    ChatProc --> BibleDB
    ChatProc --> MiniMax

    ImageGen --> MiniMaxImg
    ImageGen --> OpenAI

    Moderation --> OpenAI
    VerseVal --> BibleDB

    style Vercel fill:#e1f5fe
    style Client fill:#f3e5f5
    style External fill:#fff3e0
    style Data fill:#e8f5e9
```

---

## Component Details

### Client Layer
- **Browser**: Loads static HTML/JS chat interface
- **No build step**: Pure static files served directly

### API Layer (Serverless)
- **FastAPI**: Handles HTTP requests
- **Endpoints**: `/`, `/chat`, `/generate-image`, `/health`
- **Error handling**: Graceful 500 responses with details

### Core Modules

| Module | Purpose |
|--------|---------|
| `chat.py` | Main RAG pipeline - orchestrates all processing |
| `moderation.py` | Input/output content filtering |
| `tricky_scenarios.py` | Adversarial prompt detection |
| `verse_validator.py` | Fake verse detection |
| `image_gen.py` | Image generation with safety checks |
| `bible_db.py` | Bible verse lookup & search |
| `minimax_client.py` | MiniMax API client |

### External Services

| Service | Usage |
|---------|-------|
| MiniMax API | LLM chat completions |
| MiniMax Image | Image generation |
| OpenAI API | Content moderation |

### Data Storage

| Store | Type | Purpose |
|-------|------|---------|
| `kjv_bible.json` | JSON file | 31K Bible verses |
| In-memory dict | RAM | Conversation history |
