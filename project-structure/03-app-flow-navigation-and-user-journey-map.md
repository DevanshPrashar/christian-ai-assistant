# App Flow — Navigation & User Journey Map

**Every page, every click, every path — mapped before a single screen is built.**

---

## Pages List

| Path | Description |
|------|-------------|
| `/` | Landing page — app intro and "Start Chatting" CTA |
| `/chat` | Main chat interface — where users interact with the assistant |
| `/about` | About the app — methodology, safety approach, disclaimers |

---

## Navigation Type

- **Primary:** Top navbar with links to Home, Chat, About
- **Mobile:** Collapsible hamburger menu
- **No sidebar** — single-flow application

---

## First Screen (Landing Page)

A first-time visitor sees:
- App name and tagline ("A faithful AI companion...")
- Brief description of capabilities
- "Start Chatting" primary CTA button
- Footer with disclaimer about AI limitations

---

## Auth Flow

- **v1:** No authentication
- **Future:** User accounts with conversation history and denomination preferences

---

## Core User Journey 1: Ask a Theological Question

1. User navigates to `/chat`
2. User types question in input field (e.g., "What does the Bible say about love?")
3. System validates input via moderation
4. System retrieves relevant Bible verses via RAG
5. System generates grounded response with citations
6. Response displayed with formatted text and verse references
7. User can ask follow-up questions (conversation memory active)

---

## Core User Journey 2: Generate a Christian Image

1. User types image request in chat (e.g., "Generate an image of a cross at sunset")
2. System validates prompt via moderation
3. System sends approved prompt to DALL-E 3
4. Generated image displayed in chat
5. User can download or share image

---

## Core User Journey 3: Handle Fake Verse

1. User types question with incorrect scripture (e.g., "What does John 3:16 say about X?")
2. System cross-references against Bible database
3. Fake verse detected → System responds: "I cannot verify this scripture reference. John 3:16 actually says..."
4. System provides correct verse as alternative

---

## Empty States

- **Chat page with no messages:** Welcome message with suggested questions (e.g., "Ask me about the Bible, faith, or generate Christian content")
- **Image generation in progress:** Loading spinner with "Creating your image..."

---

## Error States

| Scenario | User Message |
|----------|--------------|
| API rate limit | "Please wait a moment — I'm getting a lot of requests right now |
| Moderation flagged | "I can't respond to that — please rephrase your question |
| Image generation failed | "Sorry, I couldn't generate that image. Try a different prompt |
| Bible verse not found | "I cannot verify this scripture reference" + correction offer |

---

## Redirects

- `/` → `/chat` (on "Start Chatting" click)
- `/about` → `/chat` (on "Try It" button)
- No authenticated redirects needed for v1

---

*Part of SoluLab Project Documentation*
