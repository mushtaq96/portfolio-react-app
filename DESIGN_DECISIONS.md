# Design Decisions

Lightweight ADR-style log. Each entry states the **context**, the **decision**,
the **trade-off accepted**, and — where relevant — **what production would
require instead**. The goal is to make the reasoning inspectable, including where
it is knowingly imperfect.

A backend/platform interviewer cares less about *what* you picked than about
whether you knew what you were giving up. Every entry below names its cost.

---

## ADR-001 — Dedicated embedding microservice

**Context.** Render's free tier caps a service at 512 MB RAM. The main backend
already loads ChromaDB, the Groq client, and FastAPI. Loading a sentence-
transformer model into the same process risked OOM on cold start.

**Decision.** Split embedding into its own FastAPI service, so model memory is
isolated from the request-serving backend.

**Trade-off accepted.**
- Added a network hop and a second cold-start on the critical path.
- Two services to deploy, monitor, and keep in sync on model choice.
- The backend still keeps a *fallback* in-process embedding path, so the memory
  win is real only when the remote path is used.

**Was it justified?** For the stated constraint (staying under 512 MB on free
infra), yes — isolating a memory-heavy dependency behind a service boundary is a
legitimate platform pattern. **But** at this scale a single service with lazy
model loading would also have worked and removed a hop. The split is defensible,
not obligatory; I'd call it out as such in an interview rather than oversell it
as "scalability."

**Production alternative.** Keep the split (it becomes genuinely useful once
embedding is CPU-bound and needs independent scaling), but put the model behind a
warm pool or a managed embedding endpoint, and cache embeddings.

---

## ADR-002 — Model: `all-MiniLM-L6-v2` over multilingual L12

**Context.** The knowledge base is bilingual (EN/DE). The obvious multilingual
choice, `paraphrase-multilingual-MiniLM-L12-v2`, is ~900 MB.

**Decision.** Use the English `all-MiniLM-L6-v2` (~175 MB, 384-dim) for both
languages.

**Trade-off accepted.** German retrieval quality is weaker than a true
multilingual model would give. The bet is that for a small, structured CV corpus
the semantic gap is tolerable.

**Honesty gap to close.** This bet is currently **unmeasured**. The credible
version of this decision includes a handful of German test queries with the
retrieved chunks eyeballed for relevance. Claiming "reasonable German support"
without that evidence is exactly the kind of unverified claim a Swiss interviewer
will probe. Measure it, or soften the claim.

**Cleanup owed.** The L12 model is still committed to the repo but never loaded.
Remove it.

---

## ADR-003 — Retrieval: fixed-size character chunking, top-3, no re-ranking {#retrieval}

**Context.** The corpus is a few short documents. Full RAG machinery (semantic
chunking, hybrid search, re-rankers) would be disproportionate.

**Decision.** 1000-character fixed windows, cosine top-3, context concatenated
verbatim.

**Trade-off accepted.** Fixed windows cut mid-word and mid-sentence, which
degrades embedding quality at chunk boundaries. Top-3 with no re-ranking can miss
the best chunk when documents overlap.

**Right-sized?** Yes for this corpus — over-engineering retrieval here would be a
red flag, not a green one. The one cheap improvement worth making is sentence-
aware chunking (split on paragraph/sentence, then pack to a size budget); it
removes the mid-word artifact for near-zero cost.

---

## ADR-004 — Groq + Llama 3.1 8B, non-streaming, `max_tokens=200`

**Context.** Needed a fast, free/cheap inference endpoint.

**Decision.** Groq's hosted Llama 3.1 8B. Non-streaming. Short answer cap.

**Trade-off accepted.** `max_tokens=200` truncates longer answers. Non-streaming
means the user stares at "Thinking…" for the full generation, which on top of a
cold start feels slow.

**Production alternative.** Stream tokens (turns perceived latency from
"total" into "time-to-first-token"). Keep the small model — it's the right call
for cost and speed at this scale.

---

## ADR-005 — Access control: open endpoint + best-effort rate limit {#access-control}

**Context.** A portfolio has no user accounts. The chat endpoint spends real
money (Groq quota).

**Decision.** No auth; `CORS: *`; an in-memory, IP-keyed limiter of 5 req/hour.

**Trade-off accepted — and this one is under-priced.** The limiter:
- resets on every restart/deploy,
- is not shared across instances,
- and behind Render's proxy keys on the **proxy IP**, not the caller — so it
  either throttles everyone together or can be bypassed.

In other words, the documented protection does not reliably hold. For a demo the
blast radius is "someone burns my free Groq quota," which is survivable — but the
README should not imply this is real abuse protection.

**Production alternative (right-sized, not enterprise).** A shared counter in
Redis keyed on the real client IP (`X-Forwarded-For`, validated), or a single
signed token the frontend obtains and sends. `slowapi` gives most of this in a
few lines. This is a small change, not a big one — which is why leaving it broken
is a weak spot rather than a defensible trade-off.

---

## ADR-006 — Voice is client-side (Web Speech API) {#voice}

**Context.** Wanted voice input/output without running Whisper or a TTS service.

**Decision.** Use the browser's `SpeechRecognition` and `speechSynthesis`. No
audio touches the server.

**Trade-off accepted.** Browser support is uneven (best in Chrome), and voice
quality/behaviour varies by platform. In exchange: zero server cost, zero audio
handling, zero privacy surface.

**Verdict.** Correct call for the constraints. The mistake attached to it is that
`openai-whisper` — the server-side path this decision *replaced* — is still in
`backend/requirements.txt`, inflating build time and implying capability that
doesn't exist. Remove it.

---

## ADR-007 — Generated artifacts committed to git {#artifacts}

**Context.** Render builds from the repo. To avoid runtime downloads, the
ChromaDB index and model weights were committed (via Git LFS).

**Decision as it stands.** `.chroma_db/` and model files live in the repository.

**Why this is the weakest decision in the project.**
- The vector DB is a *build output* of `build.py`; committing it means the repo
  and the code that generates it can silently diverge.
- Model weights via LFS are stored as pointers; deployment then depends on
  free-tier LFS bandwidth, an invisible failure mode.
- `.gitignore` lists `.chroma_db/` while the files are simultaneously tracked —
  an internal contradiction that signals the rule was added after the fact.

**Correct approach (still simple).** Generate the index at deploy time (a build
step running `build.py`), and let the embedding model download on first boot or
be baked into a container image. Treat data and weights as artifacts, never as
source.

---

## ADR-008 — Personal documents in the repository

**Context.** RAG needs the source documents; they were placed in
`backend/.documents/`.

**Decision as it stands.** Real CV/profile PDFs (including a Lebenslauf) are
committed to a public repo.

**Assessment.** This is a privacy issue, not a design trade-off. PII in git
history is effectively permanent. The documents should be supplied out of band
(local dir, object storage, or a private submodule) and scrubbed from history.
There is no upside to accept here — it's simply owed cleanup.

---

## Decision scorecard

| ADR | Decision | Verdict |
|---|---|---|
| 001 | Embedding microservice | Defensible, not obligatory — say so |
| 002 | Small English model for DE too | Reasonable bet, **currently unmeasured** |
| 003 | Simple chunking/retrieval | Right-sized; add sentence-aware chunking |
| 004 | Groq 8B, non-streaming | Good model choice; stream next |
| 005 | Open endpoint + weak limiter | **Under-priced risk; cheap to fix** |
| 006 | Client-side voice | Correct; delete the dead Whisper dep |
| 007 | Artifacts in git | **Weakest decision; reverse it** |
| 008 | PII in git | Not a trade-off; remediate |

The pattern worth noticing: the *architecture* decisions (001–004, 006) are
sound and constraint-aware. The *hygiene* decisions (005, 007, 008) are where the
project loses credibility. That's a good problem to have — hygiene is faster to
fix than architecture is to redesign.
