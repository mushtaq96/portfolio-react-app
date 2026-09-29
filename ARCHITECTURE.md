# Architecturee

This document describes what the system **is** today, not an aspirational
version of it. Known gaps are called out inline and collected at the end.

## 1. Overview

The system is a static frontend plus two small stateless-ish HTTP services and a
local vector store. It implements a standard RAG loop over a small, private
document set (my CV and profile, EN + DE).

```
                      ┌─────────────────────────────┐
                      │  Browser (GitHub Pages)     │
                      │  React SPA + chat widget    │
                      │  Web Speech API (STT/TTS)   │
                      └──────────────┬──────────────┘
                                     │ HTTPS  POST /api/chat
                                     ▼
                      ┌─────────────────────────────┐
                      │  Backend  (Render, FastAPI) │
                      │  - CORS, rate-limit mw       │
                      │  - RAG orchestration         │
                      └───┬───────────────┬──────────┘
              /embed      │               │  chat.completions
                          ▼               ▼
        ┌─────────────────────────┐   ┌────────────────────┐
        │ Embedding API (Render)  │   │  Groq API          │
        │ sentence-transformers   │   │  Llama 3.1 8B      │
        │ all-MiniLM-L6-v2        │   └────────────────────┘
        └─────────────────────────┘
                          │ vectors
                          ▼
        ┌─────────────────────────┐
        │ ChromaDB (persistent,   │
        │ local to backend)       │
        └─────────────────────────┘
```

## 2. Components

### 2.1 Frontend (`frontend/`)
- React 18 SPA built with Create React App, styled with Tailwind.
- Deployed to GitHub Pages via GitHub Actions on push to `main`.
- Chat widget (`components/Chatbot/ChatWindow.jsx`) posts to `/api/chat`.
- Voice is **fully client-side**: `SpeechRecognition` for input,
  `speechSynthesis` for output. No audio ever reaches the server. This is a
  deliberate cost/complexity decision (see DESIGN_DECISIONS §Voice).
- Resolves the backend URL from `REACT_APP_API_BASE_URL`, with a hardcoded
  production fallback.

### 2.2 Backend (`backend/`)
FastAPI app (`main.py`). Responsibilities:
1. **CORS + rate-limit middleware.** IP-keyed, in-memory, 5 req/hour on
   `/api/chat`.
2. **Embedding.** Calls the Embedding API's `/embed` if `EMBEDDING_API_URL` is
   set; otherwise falls back to ChromaDB's in-process embedding function.
3. **Retrieval.** `chroma_collection.query(..., n_results=3)`, run in a worker
   thread so it does not block the event loop. A short follow-up ("and
   Kubernetes?") is retrieved together with the previous user question.
4. **Prompt assembly.** A system message (`prompts.py` instruction + language
   constraint + retrieved context), then the last 6 conversation turns from
   `history`, then the question. UI-only messages (welcome, error bubbles) are
   dropped.
5. **Generation.** Groq `chat.completions` (in a worker thread),
   `llama-3.1-8b-instant`, `max_tokens=200`, non-streaming.
6. **Health.** `GET /` and `GET /health`.
7. **Indexing (guarded).** `POST /api/index-documents` exists only when
   `ALLOW_INDEXING=true`, to prevent accidental re-index in production.

### 2.3 Embedding API (`embedding_api/`)
Separate FastAPI service whose only job is `POST /embed → vectors`.
- Model: `sentence-transformers/all-MiniLM-L6-v2` (384-dim).
- Loaded once via a thread-safe singleton (`embedding_service.py`,
  double-checked locking).
- `get_embedding` is memoized with `lru_cache(maxsize=512)`.
- `/health` reports model load status.

### 2.4 Vector store (ChromaDB)
- `PersistentClient` writing to `backend/.chroma_db`.
- One collection, `portfolio_docs`, of ~fixed-size character chunks with
  `{language, source_doc}` metadata.
- Built offline by `backend/build.py` from `backend/.documents/{English,German}`.

## 3. Request lifecycle: `POST /api/chat`

1. Middleware checks the caller's request count for the hour; rejects with 429 if
   over the limit.
2. Handler embeds the question — remote Embedding API if configured, else local.
3. Vector search returns the top 3 chunks; they are concatenated into a context
   block (or a "no relevant information" sentinel).
4. `prompts.py` selects a base instruction (general vs. "value" question),
   applies a language constraint, and assembles the final prompt.
5. Groq generates the answer; the handler returns `{response, context}`.
6. Failures map to real status codes: 502 when embedding, vector search or the
   LLM fails; 503 when the knowledge base or LLM client did not load; 429 from
   the rate limiter; 422 for invalid input (empty or over-long message, unknown
   language). Error details are logged, never returned to the caller.

## 4. Deployment topology

| Unit | Host | Trigger | Notes |
|---|---|---|---|
| Frontend | GitHub Pages | Actions on push to `main` | `CI: false` in the workflow |
| Backend | Render free web service | Git push | Sleeps when idle |
| Embedding API | Render free web service | Git push | Sleeps when idle |
| Groq | External SaaS | — | Rate/cost governed by Groq |

**Cold-start consequence:** a first chat after idle can pay two sequential cold
starts (backend, then embedding). This is the dominant latency factor and is a
property of the free tier, not the code.

## 5. Data & configuration

- **Secrets:** `GROQ_API_KEY` via environment only; `.env` is gitignored.
- **Config:** `EMBEDDING_API_URL`, `ALLOW_INDEXING`, `EMBEDDING_MODEL_NAME`.
- **Generated data:** `.chroma_db/` and the embedding model weights are build
  artifacts and should be produced at build/deploy time, not committed (see
  DESIGN_DECISIONS §"Generated artifacts in git").
- **Source documents:** `backend/.documents/` contains personal PDFs. These are
  PII and should not live in a public repository (see Known Limitations).

## 6. Known limitations (architectural)

1. **Unauthenticated LLM proxy.** `/api/chat` is open and `CORS` is `*`. The only
   guard is an in-memory rate limiter (5 requests/hour per client IP) that resets
   on restart and is not shared across instances. It reads the client IP from
   `X-Forwarded-For`, counted from the right by `TRUSTED_PROXY_COUNT` (default 1).
   **That value has not been verified against Render's real proxy chain**; if it
   is wrong, clients share a bucket or the limit is bypassable.
2. **Two failure-prone external hops per request** (embedding service + Groq),
   each on the critical path, with no caching of full answers.
3. **State that pretends to be shared isn't.** The rate-limit map is per-process;
   with more than one instance the limit is effectively multiplied.
4. **Basic multi-turn.** Recent turns are sent to the LLM, but there is no
   summarisation or LLM-based query rewriting.
5. **Deprecated frontend tooling.** CRA is end-of-life (use Vite).

Fixed since the first version of this document: conversation history is now used;
upstream failures return 502/503 instead of 200 with an embedded error string;
the limiter returns a real 429 (it used to surface as a 500) and keys on the
client IP rather than the proxy's; blocking calls no longer run on the event
loop; startup uses a lifespan handler; raw retrieved chunks are no longer returned
to callers unless `DEBUG_CONTEXT=true`.

## 7. What this architecture is appropriate for

A single-author portfolio with a tiny, static knowledge base and near-zero
traffic. The design is **constraint-first**: every choice is bounded by "free
tier, one developer, must stay up cheaply." It is explicitly *not* sized for
concurrent users, private data, or an SLA — and the remediation for each of those
is documented rather than pre-built. See DESIGN_DECISIONS.md for the reasoning
behind each boundary.
