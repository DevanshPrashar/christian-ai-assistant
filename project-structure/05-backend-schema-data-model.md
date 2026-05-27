# Backend Schema — Data Model & Auth Architecture

**How your data is stored, structured, and secured — defined before the AI writes a single migration.**

---

## Table: conversations

Stores conversation history per user session.

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT (UUID) | Primary key |
| created_at | TIMESTAMP | When conversation started |
| updated_at | TIMESTAMP | Last message timestamp |
| denomination | TEXT | User's preferred denomination |
| is_active | BOOLEAN | Flag for active conversations |

---

## Table: messages

Individual messages within a conversation.

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT (UUID) | Primary key |
| conversation_id | TEXT (FK) | References conversations.id |
| role | TEXT | "user" or "assistant" |
| content | TEXT | Message content |
| created_at | TIMESTAMP | When message was sent |
| metadata | TEXT (JSON) | Additional data (e.g., referenced verses) |

---

## Table: bible_verses

Pre-loaded Bible verse database for RAG.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| book | TEXT | e.g., "John" |
| chapter | INTEGER | Chapter number |
| verse | INTEGER | Verse number |
| text | TEXT | Full verse text |
| embedding | TEXT | Pre-computed vector embedding |

---

## Table: image_generations

Logs of generated images for audit.

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT (UUID) | Primary key |
| conversation_id | TEXT (FK) | References conversations.id |
| prompt | TEXT | Original user prompt |
| approved_prompt | TEXT | Moderation-approved prompt |
| image_url | TEXT | Generated image URL |
| created_at | TIMESTAMP | Generation timestamp |

---

## Relationships

```
conversations.id (1) ─────< messages.conversation_id (many)
conversations.id (1) ─────< image_generations.conversation_id (many)
```

---

## Auth Model

**v1:** No authentication — public demo
- Conversations identified by session ID in localStorage
- No user accounts or persistent identity

**v2 (future):** Supabase Auth with email + Google OAuth
- User accounts with persistent history
- Per-user denomination preferences

---

## User Roles (v2)

| Role | Access |
|------|--------|
| guest | Can chat and generate images, no history persistence |
| user | Full access with persistent history |
| admin | Full access + analytics dashboard |

---

## Sensitive Fields

- **API Keys:** Stored in `.env`, never in database
- **Message content:** Not encrypted (public demo), would encrypt in production
- **Image URLs:** Stored as-is (external service URLs)

---

## File Storage

- **Images:** Stored via OpenAI/DALL-E external URL (not locally stored)
- **Bible data:** `data/kjv_bible.json` — static JSON file
- **Vector DB:** Chroma in-memory or local persistent volume

---

*Part of SoluLab Project Documentation*
