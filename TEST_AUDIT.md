# Test Audit

> **Status update.** F1–F5 below were fixed in `2b615f0` and the suite now runs
> (7 tests passed locally). The correctness bug it describes (HTTP 200 on every
> upstream failure) and the 429-vs-500 rate-limit question were then fixed on
> `fix/backend-correctness`, with tests that lock each behaviour in: 35 tests pass
> locally, and 27 of them fail against the previous `main.py`, so they test real
> behaviour. The findings below are kept as the record of what was wrong.

**Method:** static analysis of the test suite against the code it targets, at the
current `main`. It has not been executed in this audit (the heavy backend
dependencies — torch, chromadb, sentence-transformers, whisper — were not
installed), but every finding below is a concrete, line-referenced mismatch
between test and implementation that would fail deterministically on run.
Nothing here is a judgement call.

**Bottom line:** the suite cannot pass as written. It gives the *appearance* of
test coverage while asserting against APIs the code no longer uses. This is a
credibility liability, not an asset — a reviewer who reads it learns the tests
haven't been run in a long time.

---

## Inventory

| File | Tests | State |
|---|---|---|
| `tests/conftest.py` | 4 fixtures (3 autouse) | Broken fixture blocks the whole suite |
| `tests/test_main.py` | `test_chat_api` | Runs, but asserts nothing meaningful |
| `tests/test_document_processor.py` | `test_initialize_collection`, `test_process_pdf` | Both wrong against current code |

There is **no** frontend test beyond the CRA default, and **no** test for the
embedding API at all.

---

## Findings (ranked by impact)

### F1 — `conftest.py` patches a symbol that no longer exists  🔴 blocks everything
`tests/conftest.py:28-31`:
```python
@pytest.fixture(scope="session", autouse=True)
def mock_whisper():
    with patch('main.whisper.load_model') as mock:
        ...
```
`main.py` does not import `whisper` (voice moved to the browser; see
DESIGN_DECISIONS ADR-006). This autouse, session-scoped fixture runs for every
test and will raise `AttributeError: module 'main' has no attribute 'whisper'`
(or `ModuleNotFoundError`) at setup, taking the entire suite down before any
assertion executes.

**Fix:** delete the fixture. It's a fossil of a removed feature.

---

### F2 — `test_process_pdf` asserts the wrong ChromaDB method  🔴 will fail
`tests/test_document_processor.py:43-44`:
```python
process_pdf(mock_client, str(pdf_path))
mock_client.add.assert_called_once()
```
`document_processor.process_pdf` calls `collection.upsert(...)`
(`document_processor.py:97`), never `.add()`. The assertion fails even if the
test is reached.

**Fix:** assert on `upsert`, and assert on its arguments (ids, chunk count),
not merely that it was called.

---

### F3 — `test_initialize_collection` patches the wrong client class  🟠 ineffective / slow
`tests/test_document_processor.py:29`:
```python
with patch('chromadb.Client', return_value=mock_client):
```
`initialize_collection` uses `chromadb.PersistentClient`
(`document_processor.py:21`), not `chromadb.Client`. The patch is inert: the real
`PersistentClient` runs and tries to construct a
`SentenceTransformerEmbeddingFunction`, pulling in a model. The test either does
real I/O or fails for reasons unrelated to what it claims to check.

**Fix:** patch `document_processor.chromadb.PersistentClient` and the embedding
function at the point of use.

---

### F4 — `test_chat_api` is a tautology  🟠 passes but proves nothing
`tests/test_main.py:5-11` asserts `status_code == 200` and that `response`/
`context` keys exist. But `/api/chat` returns **200 on every path**, including
internal errors (it embeds the error string in `context`). So the test passes
whether the RAG pipeline works or is completely broken.

**Fix:** two changes, together. First, make the endpoint return correct status
codes (5xx on upstream failure) — see the correctness note below. Then assert on
behaviour: mock Groq and the embedding call, and check the returned answer
reflects the injected context.

---

### F5 — Autouse mocks don't cover the real dependencies  🟠 hidden real calls
`conftest.py` mocks `chromadb.Client` and the embedding function, but `main.py`'s
startup uses `chromadb.PersistentClient(...).get_collection(...)` and a real
`groq.Groq(...)` client. Under test, startup either fails (no collection) or the
handler makes real network calls to Groq if a key is present. The mocks give a
false sense that externals are isolated; they aren't.

**Fix:** patch at the import site (`main.chromadb.PersistentClient`,
`main.groq_client`) and inject a fake collection + fake Groq response.

---

## A correctness bug the tests should have caught (but couldn't)

Because F4 accepts any 200, it masks a real design smell: **`/api/chat` swallows
upstream failures and returns 200.** Embedding-service and Groq errors come back
as a friendly message with the error in `context`. That breaks HTTP semantics,
hides failures from any monitoring, and is precisely why the happy-path test is
worthless. A corrected endpoint returns 5xx on upstream failure; a corrected test
then has something real to assert.

This is the value of a real suite: it would have forced the status-code question.

---

## Remediation plan (small, ordered, right-sized)

Do these in order; each is cheap and the payoff front-loads.

1. **Delete `mock_whisper`** (F1). Unblocks the suite. ~2 minutes.
2. **Fix `test_process_pdf`** to assert `upsert` + args (F2).
3. **Fix the patch targets** in `test_document_processor.py` and `conftest.py` to
   the real classes at their import sites (F3, F5).
4. **Make `/api/chat` return correct status codes**, then rewrite `test_chat_api`
   to mock embedding + Groq and assert on the answer (F4, correctness bug).
5. **Add one embedding-API test** (`POST /embed` returns a vector of the expected
   dimension for a known input).
6. **Wire `pytest` into GitHub Actions** on push and PR. Until this exists, none
   of the above stays fixed — see LESSONS_LEARNED §1.

**Explicitly out of scope** (would be over-engineering at this stage): coverage
gates, property-based testing, load tests, contract tests between services. A
handful of tests that *actually run in CI* is the right target here — not a test
pyramid for a single-author portfolio.

---

## Suggested minimal CI (for step 6)

```yaml
# .github/workflows/backend-tests.yml
name: backend-tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    defaults: { run: { working-directory: backend } }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -r requirements.txt
      - run: pytest -q
```

The moment this is green on a real run, the suite stops being a liability and
starts being evidence. That transition — from "tests exist" to "tests run and
gate merges" — is the single highest-leverage change in the whole repository.
