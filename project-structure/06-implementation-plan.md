# Implementation Plan — Step-by-Step Build Sequence

**The exact order to build so the AI never skips a foundation layer.**

---

## Phase 1: Setup

- [ ] Initialize project folder structure per TRD
- [ ] Create `requirements.txt` with all dependencies
- [ ] Create `.env.example` with required API key variables
- [ ] Set up GitHub repo with `.gitignore`
- [ ] Create `README.md` with project overview

**Done Criteria:** `pip install -r requirements.txt` succeeds, project runs locally

---

## Phase 2: Bible Database

- [ ] Download/obtain KJV Bible JSON (public domain)
- [ ] Create `data/kjv_bible.json` with book/chapter/verse/text
- [ ] Create `src/bible_db.py` with verse lookup functions
- [ ] Pre-compute embeddings for all verses (sentence-transformers)
- [ ] Initialize ChromaDB with verse collection

**Done Criteria:** Can query "John 3:16" and get correct text back

---

## Phase 3: Moderation Layer

- [ ] Implement input moderation check in `src/moderation.py`
- [ ] Implement output moderation check
- [ ] Create denial response templates
- [ ] Test with known problematic prompts

**Done Criteria:** Blocked prompts return graceful denial, not crash

---

## Phase 4: Chat API

- [ ] Create `src/main.py` with FastAPI setup
- [ ] Implement `/chat` endpoint with RAG pipeline
- [ ] Implement verse grounding (retrieve → inject → respond)
- [ ] Add conversation memory (in-memory context)
- [ ] Test scripture grounding with sample questions

**Done Criteria:** Response includes at least 1 verifiable Bible verse citation

---

## Phase 5: Image Generation

- [ ] Implement `/generate-image` endpoint
- [ ] Add prompt moderation before sending to DALL-E
- [ ] Connect DALL-E 3 API
- [ ] Return image URL in response
- [ ] Test with safe Christian prompts

**Done Criteria:** "Generate an image of a cross" returns appropriate image

---

## Phase 6: Tricky Scenarios

- [ ] Implement fake verse detection (cross-ref against DB)
- [ ] Add denominator-aware system prompts
- [ ] Create denial handling for adversarial prompts
- [ ] Implement "I cannot verify" responses for hallucinated verses

**Done Criteria:** Fake verse query returns "I cannot verify" + correction

---

## Phase 7: Frontend

- [ ] Create `static/index.html` chat UI
- [ ] Implement JavaScript chat interaction
- [ ] Apply styling per UI/UX Design Brief
- [ ] Add dark/light mode toggle
- [ ] Test end-to-end from browser

**Done Criteria:** User can chat and receive responses in browser

---

## Phase 8: Evaluation Dataset

- [ ] Create `tests/edge_case_prompts.json`
- [ ] Create `tests/adversarial_prompts.json`
- [ ] Create `tests/hallucination_test_cases.json`
- [ ] Test each category manually.

**Done Criteria:** All 3 test files exist with 5+ prompts each

---

## Phase 9: Polish & Documentation

- [ ] Write architectural decision notes
- [ ] Complete README.md with setup instructions
- [ ] Verify all features against PRD checklist
- [ ] Final code cleanup

**Done Criteria:** Repo is presentable, demo runs without errors

---

## Done Criteria: What "Finished" Looks Like

1. All core features from PRD work end-to-end
2. Scripture citations verified against Bible database
3. Fake verses caught and handled gracefully
4. Adversarial prompts blocked with helpful denial
5. Images generate for safe Christian prompts
6. Chat interface is usable and renders correctly
7. Demo completed within 5 hours total

---

*Part of SoluLab Project Documentation*
