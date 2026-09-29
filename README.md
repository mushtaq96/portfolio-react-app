# Portfolio Website with a RAG Chatbot

A personal portfolio site with an AI assistant that answers questions about my
background. The assistant uses Retrieval-Augmented Generation (RAG): my CV and
profile documents are chunked, embedded, and stored in a vector database; at
query time the most relevant chunks are retrieved and passed to an LLM as
grounding context.

> **Status:** working demo, deployed on free-tier infrastructure. This is a
> personal project, not a production service. Known limitations are listed
> explicitly below rather than hidden — see [Limitations](#limitations).

- **Live demo:** <!-- TODO: paste the GitHub Pages URL. Note free-tier cold start below. -->
- **Architecture:** see [ARCHITECTURE.md](ARCHITECTURE.md)
- **Why it's built this way:** see [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md)
- **What I'd change:** see [LESSONS_LEARNED.md](LESSONS_LEARNED.md)

<!-- TODO: add a screenshot or GIF of the chat in action here. A recruiter
     spends ~15s on a repo; a picture buys you the next 15. -->

---

## What it does

- Static single-page portfolio (React + Tailwind), hosted on GitHub Pages.
- A chat widget that answers questions about my experience, grounded in my own
  CV/profile documents (English and German).
- Bilingual: the user picks EN or DE; the answer is constrained to that language.
- Voice input and spoken replies via the browser's Web Speech API (no server-side
  audio processing).

## How it works (1-minute version)

```
Browser ──POST /api/chat──▶ Backend (FastAPI)
                              │  1. embed the question   ──▶ Embedding API (FastAPI + sentence-transformers)
                              │  2. vector search        ──▶ ChromaDB (local, persisted)
                              │  3. build grounded prompt
                              └─ 4. generate answer      ──▶ Groq (Llama 3.1 8B)
```

Three deployable units:

| Service | Stack | Host | Role |
|---|---|---|---|
| `frontend/` | React 18, Tailwind, CRA | GitHub Pages | UI + chat widget |
| `backend/` | FastAPI, ChromaDB, Groq client | Render (free) | RAG orchestration, LLM call |
| `embedding_api/` | FastAPI, sentence-transformers | Render (free) | Turns text into vectors |

Full data flow and rationale in [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Running it locally

Prerequisites: Node 20 + Yarn, Python 3.9+, a free [Groq](https://groq.com) API key.

### 1. Embedding API (`:8001`)
```bash
cd embedding_api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```
The embedding model is downloaded on first run (see
[DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) on why weights are **not** committed).

### 2. Backend (`:8000`)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in GROQ_API_KEY
uvicorn main:app --reload --port 8000
```

Environment variables (`backend/.env`):
```
GROQ_API_KEY=...              # required
EMBEDDING_API_URL=http://localhost:8001   # optional; falls back to in-process embedding
ALLOW_INDEXING=false          # set true only when (re)building the index
TRUSTED_PROXY_COUNT=1         # reverse proxies in front of the app (client IP for rate limiting)
DEBUG_CONTEXT=false           # true returns the raw retrieved chunks in /api/chat responses
```

### 3. Build the vector index (one-off)
Place documents in `backend/.documents/English/` and `backend/.documents/German/`,
then:
```bash
cd backend && python build.py
```
This writes `backend/.chroma_db/`. That directory is **generated, not committed** —
see [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md).

### 4. Frontend (`:3000`)
```bash
cd frontend
yarn install
REACT_APP_API_BASE_URL=http://localhost:8000 yarn start
```

### Smoke test
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is your cloud experience?", "language": "en"}'
```

---

## Testing

```bash
cd backend && pytest
```

> **Honest note:** the current test suite does not pass and does not reflect the
> code it claims to test. This is documented, with a remediation plan, in
> [TEST_AUDIT.md](TEST_AUDIT.md). I'd rather show the audit than a green badge I
> haven't earned.

---

## Limitations

These are deliberate trade-offs of a free-tier personal project, stated up front:

- **Cold starts.** Both backend services sleep on Render's free tier. The first
  request after idle can take 30–60s *per service*. Acceptable for a portfolio,
  not for production.
- **The chat endpoint is unauthenticated.** Rate limiting (5 questions/hour per
  client IP) is best-effort and in-memory: it resets on restart, and the proxy
  assumption behind the client-IP lookup (`TRUSTED_PROXY_COUNT`) is unverified on
  Render. See [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md#access-control).
- **Basic multi-turn.** The last 6 turns are sent to the LLM and short follow-ups
  reuse the previous question for retrieval. There is no summarisation or
  LLM-based query rewriting.
- **Retrieval is deliberately simple.** Fixed-size character chunking, top-3
  cosine retrieval, no re-ranking. Good enough for a handful of CV documents;
  see [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md#retrieval).

## Roadmap

1. Verify `TRUSTED_PROXY_COUNT` against the deployed proxy chain, and add a
   lightweight token on the chat endpoint.
2. Migrate the frontend from CRA to Vite.
3. Stream LLM responses.

## License

<!-- TODO: add a LICENSE file, or remove this section. The old README claimed MIT
     without shipping the file. -->

---

*Design intent and trade-offs are documented in the companion files linked above.
That documentation is part of the project on purpose: for a backend/platform
role, the reasoning is the artifact.*
