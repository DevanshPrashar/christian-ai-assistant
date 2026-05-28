# Architecture Diagram - C1 & C2 Views

---

## C1: Context Diagram

```mermaid
graph LR
    User(("👤 User")) -->|HTTP/HTTPS| App["Christian AI<br/>Assistant<br/>(Vercel)"]
    App -->|API Calls| MiniMax["MiniMax API"]
    App -->|API Calls| OpenAI["OpenAI API<br/>(Moderation)"]

    Admin(("👨‍💻 Developer")) -->|Deploy/Manage| App

    style App fill:#2196F3,color:#fff
    style MiniMax fill:#FF9800
    style OpenAI fill:#9C27B0,color:#fff
    style User fill:#4CAF50,color:#fff
    style Admin fill:#607D8B,color:#fff
```

### C1 Description

| Component | Type | Description |
|-----------|------|-------------|
| User | External Actor | End user accessing via browser |
| Christian AI Assistant | System | The deployed application on Vercel |
| MiniMax API | External System | LLM chat & image generation |
| OpenAI API | External System | Content moderation |
| Developer | External Actor | Deploys and manages the system |

---

## C2: Container Diagram

```mermaid
graph TB
    subgraph Browser["🌐 Browser (Client)"]
        UI["Chat UI<br/>static/index.html"]
    end

    subgraph Vercel["☁️ Vercel Serverless"]
        subgraph FastAPI["🐍 FastAPI Application"]
            API_Routes["API Routes<br/>/chat, /generate-image<br/>/health, /"]
        end

            subgraph Chat_Service["💬 Chat Service"]
                OffTopic["Off-Topic<br/>Check"]
                Adversarial["Adversarial<br/>Detection"]
                Moderation["Content<br/>Moderation"]
                RAG["RAG Pipeline<br/>Retrieve → Augment → Generate"]
                VerseVal["Verse<br/>Validator"]
            end

            subgraph Image_Service["🖼️ Image Service"]
                ImgModeration["Prompt<br/>Safety Check"]
                MiniMaxImg["MiniMax<br/>Image API"]
                Dalle["DALL-E<br/>Fallback"]
            end

            subgraph Data["📦 Data Layer"]
                BibleDB["Bible DB<br/>kjv_bible.json"]
                Memory["Conversation<br/>Memory"]
            end
    end

    subgraph External["🔗 External Services"]
        MiniMaxLLM["MiniMax API<br/>(LLM)"]
        OpenAIMod["OpenAI API<br/>(Moderation)"]
    end

    %% Connections
    UI -->|HTTP| API_Routes
    API_Routes --> Chat_Service
    API_Routes --> Image_Service

    Chat_Service --> BibleDB
    Chat_Service --> Memory
    Chat_Service --> MiniMaxLLM
    Chat_Service --> OpenAIMod

    Image_Service --> ImgModeration
    ImgModeration --> MiniMaxImg
    MiniMaxImg -->|Fail| Dalle

    style Browser fill:#E3F2FD
    style Vercel fill:#E8F5E9
    style FastAPI fill:#FFF3E0
    style Chat_Service fill:#F3E5F5
    style Image_Service fill:#FCE4EC
    style Data fill:#E0F7FA
    style External fill:#ECEFF1
```

### C2 Components

| Container | Responsibility | Technologies |
|-----------|----------------|--------------|
| Chat UI | User interface for messaging | HTML, CSS, JavaScript |
| API Routes | HTTP request handling | FastAPI |
| Off-Topic Check | Filter non-Christian questions | Python |
| Adversarial Detection | Block jailbreak attempts | Python regex + keywords |
| Content Moderation | Filter harmful content | OpenAI API + keywords |
| RAG Pipeline | Scripture-grounded responses | Keyword search + MiniMax |
| Verse Validator | Detect fake/hallucinated verses | Python |
| Image Service | Generate Christian images | MiniMax + DALL-E |
| Bible DB | Store 31K KJV verses | JSON file |
| Memory | Conversation history | In-memory dict |

---

## Data Flow Summary

```
User Input → Off-Topic Check → Adversarial Check → Moderation
                                                        ↓
                                                    RAG Pipeline
                                                    ↓
Bible DB ← Retrieve ← Prompt + Context → MiniMax LLM
                                                    ↓
                                          Validate Response
                                                    ↓
                                          Fake Verse Check
                                                    ↓
                                          Return + Citations
```
