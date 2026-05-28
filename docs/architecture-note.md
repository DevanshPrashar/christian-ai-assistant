# Architecture Note

## Overview

The Christian AI Assistant is a serverless web application that combines RAG-based chat with image generation, deployed on Vercel.

## Architecture

```
Browser → Vercel Serverless (Python/FastAPI) → MiniMax API
                                              ↓
                                         Bible DB (KJV)
```

## Components

### Frontend
- Static HTML/JS chat interface
- Served directly from Vercel (no build step)
- Single page with dark/light mode

### API Layer (FastAPI on Vercel)
- `/` - Serves static frontend
- `/chat` - Main chat endpoint with RAG pipeline
- `/generate-image` - Image generation endpoint
- `/health` - Health check

### RAG Pipeline
1. **Retrieve**: Keyword search against 31K verse Bible database
2. **Augment**: Inject top 5 relevant verses into prompt
3. **Generate**: MiniMax-M2.7 generates response

### Safety Layers
1. **Off-topic check**: Blocks non-Christian questions
2. **Adversarial detection**: Catches jailbreak attempts
3. **Content moderation**: Keyword + theological checks
4. **Fake verse detection**: Validates citations against DB

### External APIs
- **MiniMax**: Chat completions + image generation
- **OpenAI**: Content moderation (fallback)

## Data Storage
- **Bible DB**: Static JSON file (~6.8MB, 31K verses)
- **Conversation memory**: In-memory dictionary (serverless)

## Deployment
- Platform: Vercel (serverless Python)
- Region: US East
- Cold start: ~2-3 seconds

## Performance
- Chat latency: ~1-3 seconds (depends on MiniMax)
- Image generation: ~5-10 seconds
- Bible search: <50ms (in-memory)
