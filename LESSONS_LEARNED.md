# Lessons Learned

Written in the first person, on purpose. For a senior backend/platform role — and
especially in the Swiss market, where understatement and accuracy are read as
competence — the ability to critique your own work is worth more than the work
looking flawless. This document is the interview asset. Every entry is something
I can talk through under questioning without flinching.

---

## 1. A test that never runs is worse than no test

My suite doesn't pass. The fixtures patch a `whisper` symbol the code no longer
has, and one test asserts `.add()` when the code calls `.upsert()`. That means
the tests were written once, "passed" in a moment that no longer exists, and were
never run again.

**The real lesson:** tests only mean something if CI runs them on every push. A
green suite I never execute is theatre. The fix isn't "write more tests" — it's
"run the ones I have, in CI, and let red block the merge." See
[TEST_AUDIT.md](TEST_AUDIT.md).

**What I'd do differently:** wire `pytest` into GitHub Actions *before* writing
the second test, so the discipline is enforced by the machine, not my memory.

---

## 2. I built plumbing I didn't connect

The frontend sends conversation `history`. The backend accepts it in the Pydantic
model. And then… nothing — it's never put in the prompt. I shipped a multi-turn
interface over a single-turn engine and didn't notice, because I never tested a
second turn.

**The lesson:** an API contract that accepts a field it ignores is a lie the code
tells the caller. Either use it or reject it. Half-wired features are how systems
accumulate quiet incorrectness.

---

## 3. Security theatre is a tell

My rate limiter looks like protection. It isn't: it's per-process, resets on
deploy, and behind a proxy it keys on the wrong IP. I wrote it, saw "429 works
locally," and moved on — without reasoning about how it behaves behind Render's
load balancer or across restarts.

**The lesson:** for anything security- or correctness-adjacent, I have to reason
about the *deployed topology*, not the local happy path. "It returned 429 on my
laptop" is not "it limits abuse in production." The gap between those two
statements is most of platform engineering.

---

## 4. Data and code drift when data lives in git

Committing the vector DB and model weights felt convenient — no runtime download.
But the index is an *output* of my own `build.py`, and once it's committed, the
code and the data can silently disagree. I also ended up with a `.gitignore` that
ignores the very directory git is tracking. That contradiction is a fossil of a
decision I changed my mind about but never cleaned up.

**The lesson:** build artifacts are not source. If a script produces it, a build
step should produce it — at deploy time, reproducibly. Committing generated state
trades a small convenience now for a class of "works on my machine" bugs later.

---

## 5. I leaked my own PII and called it a feature

My real CV and Lebenslauf sit in a public repo's history. RAG needs the
documents, sure — but "the app needs the data at runtime" never implied "the data
belongs in version control." Git history makes this effectively permanent.

**The lesson:** classify data before you commit it. Ask "would I be comfortable
with this in a stranger's clone in five years?" For anything personal, the answer
routes it out of the repo.

---

## 6. Dead weight accumulates when I don't prune

`openai-whisper` (large) for a voice path I moved to the browser. `reportlab` in
production deps for a single test. A whole second embedding model I never load. A
`is_devops_question()` function no caller invokes. Each was rational when added
and never removed when superseded.

**The lesson:** deletion is part of the work. Every dependency and function is a
claim about what the system does; stale claims mislead the next reader (often
future me) and slow every build.

---

## 7. My README described a more senior system than I built

The docs claimed abuse protection, implied multi-turn, and left `[X]`-second
latency placeholders and a "coming soon" screenshot. A reviewer who opens the
code before the README finds the gap immediately — and once one claim is shown
hollow, all of them are suspect.

**The lesson:** documentation is a credibility instrument. Under-claim and let
the code over-deliver, never the reverse. In Switzerland especially, a precise
"here's what works and here's what doesn't" beats a confident overstatement every
time. This whole set of documents is my correction to that habit.

---

## 8. Constraints were my best design teacher

The parts of this project I'm actually proud of all came from a hard limit: the
512 MB cap forced the embedding-service split; the free-tier cost forced client-
side voice and a small model. Constraints produced the interesting decisions. The
*absence* of a constraint — no reviewer, no CI gate, no second user — is exactly
where the sloppiness crept in.

**The lesson:** when a project has no external constraint enforcing rigor, I have
to impose one myself (CI, a checklist, a "would this survive review?" pass).
Discipline that isn't enforced by a system decays.

---

## How I'd summarize this in an interview

> "It's a working RAG chatbot on free infrastructure, and the architecture
> decisions were driven by real memory and cost constraints. The honest weak
> spots are hygiene, not design: I committed generated artifacts and PII I
> shouldn't have, my rate limiting doesn't survive the deployment topology, and
> my tests weren't running in CI so they'd rotted. I've documented each of those
> with the fix, because catching them is the actual skill the role needs."

That paragraph is the point of the project. The chatbot is the excuse to have
written it.
