# portfolio-react-app/backend/main.py
import asyncio
import logging
import os
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Annotated, List, Literal

import chromadb
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from groq import Groq
from pydantic import BaseModel, Field, StringConstraints

from prompts import get_base_instruction, is_value_question, get_language_instruction

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("portfolio.backend")

# --- Configuration -----------------------------------------------------------
MAX_REQUESTS = 5                # chat requests allowed per client...
TIME_WINDOW = 3600              # ...per this many seconds
MAX_MESSAGE_CHARS = 1000
MAX_HISTORY_TURNS = 6           # most recent conversation turns sent to the LLM
LLM_MODEL = "llama-3.1-8b-instant"
NO_CONTEXT = "No relevant information found in the knowledge base."

# Number of reverse proxies in front of this app that append to X-Forwarded-For.
# The real client is that many entries from the right; entries further left are
# client-controlled and can be spoofed. Verify this value against your host.
TRUSTED_PROXY_COUNT = int(os.getenv("TRUSTED_PROXY_COUNT", "1"))

# The chat response can include the raw retrieved chunks. That exposes source
# document text to anyone who calls the API, so it is off unless debugging.
DEBUG_CONTEXT = os.getenv("DEBUG_CONTEXT", "false").lower() == "true"

# Only enable the indexing endpoint when explicitly requested, to prevent
# accidental re-indexing in production.
ALLOW_INDEXING = os.getenv("ALLOW_INDEXING", "false").lower() == "true"

EMBEDDING_API_URL = os.getenv("EMBEDDING_API_URL")

# --- Shared resources --------------------------------------------------------
try:
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception:
    logger.exception("Could not create the Groq client; /api/chat will return 503")
    groq_client = None

# Closed in the lifespan shutdown below.
httpx_client = httpx.AsyncClient(timeout=30.0) if EMBEDDING_API_URL else None

chroma_collection = None

# In-memory, per-process rate-limit state: {client_ip: [timestamps]}.
# It resets on restart and is not shared across instances.
usage = defaultdict(list)


@asynccontextmanager
async def lifespan(_: FastAPI):
    global chroma_collection
    try:
        chroma_client = chromadb.PersistentClient(path="./.chroma_db")
        chroma_collection = chroma_client.get_collection(name="portfolio_docs")
        logger.info("ChromaDB collection 'portfolio_docs' loaded")
    except Exception:
        logger.exception("Could not load ChromaDB collection 'portfolio_docs'")
        chroma_collection = None
    yield
    if httpx_client is not None:
        await httpx_client.aclose()


app = FastAPI(lifespan=lifespan)


# --- Rate limiting -----------------------------------------------------------
def get_client_ip(request: Request) -> str:
    """Best-effort real client IP behind a fixed number of trusted proxies."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded and TRUSTED_PROXY_COUNT > 0:
        hops = [h.strip() for h in forwarded.split(",") if h.strip()]
        if len(hops) >= TRUSTED_PROXY_COUNT:
            return hops[-TRUSTED_PROXY_COUNT]
    return request.client.host if request.client else "unknown"


# Returning a response (instead of raising HTTPException) matters here: an
# exception raised inside http middleware is not handled by FastAPI's exception
# handlers and surfaces as a 500. CORS is added after this middleware, so it wraps
# it and the 429 still carries CORS headers the browser needs to read it.
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path == "/api/chat" and request.method == "POST":
        ip = get_client_ip(request)
        now = time.time()

        recent = [t for t in usage[ip] if now - t < TIME_WINDOW]
        if len(recent) >= MAX_REQUESTS:
            usage[ip] = recent
            retry_after = int(TIME_WINDOW - (now - recent[0])) + 1
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. You can only ask 5 questions per hour. "
                              "Please contact me directly for more information."
                },
                headers={"Retry-After": str(retry_after)},
            )
        recent.append(now)
        usage[ip] = recent

        # Keep the map from growing without bound with one-off visitors.
        if len(usage) > 1000:
            for stale in [k for k, v in usage.items() if not v or now - v[-1] >= TIME_WINDOW]:
                del usage[stale]

    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Indexing (opt-in) -------------------------------------------------------
if ALLOW_INDEXING:
    logger.warning("Indexing endpoint is ENABLED. Ensure this is intentional.")

    @app.post("/api/index-documents")
    async def index_documents():
        try:
            from document_processor import initialize_collection, process_document

            indexing_collection = initialize_collection()
            documents_path = ".documents"
            indexed_count = 0

            if os.path.exists(documents_path):
                for filename in os.listdir(documents_path):
                    full_path = os.path.join(documents_path, filename)
                    if os.path.isdir(full_path):
                        # A subdirectory (e.g. English, German): use its name as the language tag.
                        for sub_filename in os.listdir(full_path):
                            if sub_filename.lower().endswith((".pdf", ".docx")):
                                process_document(indexing_collection, os.path.join(full_path, sub_filename), language_tag=filename)
                                indexed_count += 1
                    elif filename.lower().endswith((".pdf", ".docx")):
                        process_document(indexing_collection, full_path)
                        indexed_count += 1

            logger.info("Indexing complete. Processed %d files.", indexed_count)
            return {"detail": f"Indexed {indexed_count} documents successfully."}
        except Exception as e:
            logger.exception("Indexing failed")
            raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


# --- Request models ----------------------------------------------------------
class MessageItem(BaseModel):
    text: str = Field(max_length=4000)
    sender: str = Field(max_length=32)


class ChatInput(BaseModel):
    message: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_MESSAGE_CHARS)
    ]
    history: List[MessageItem] = Field(default_factory=list, max_length=200)
    language: Literal["en", "de"] = "en"


# --- RAG helpers -------------------------------------------------------------
def build_history_messages(history: List[MessageItem]) -> list:
    """Map the UI's message list to LLM turns; keep only the most recent ones."""
    turns = []
    for item in history:
        if item.sender == "user":
            role = "user"
        elif item.sender == "bot":
            role = "assistant"
        else:
            continue  # welcome and error bubbles are UI text, not conversation
        turns.append({"role": role, "content": item.text[:MAX_MESSAGE_CHARS]})
    return turns[-MAX_HISTORY_TURNS:]


def build_retrieval_query(message: str, history: List[MessageItem]) -> str:
    """Short follow-ups ("and Kubernetes?") embed poorly alone, so add the previous question."""
    if len(message.split()) <= 5:
        previous = next((h.text for h in reversed(history) if h.sender == "user"), None)
        if previous:
            return f"{previous[:MAX_MESSAGE_CHARS]} {message}"
    return message


async def retrieve_context(query: str) -> str:
    """Return the top matching chunks as one string. Raises on retrieval failure."""
    if EMBEDDING_API_URL and httpx_client:
        response = await httpx_client.post(f"{EMBEDDING_API_URL}/embed", json={"texts": [query]})
        response.raise_for_status()
        embedding = response.json()["embeddings"][0]
        results = await asyncio.to_thread(
            chroma_collection.query, query_embeddings=[embedding], n_results=3
        )
    else:
        # ChromaDB embeds the text itself with the collection's embedding function.
        results = await asyncio.to_thread(
            chroma_collection.query, query_texts=[query], n_results=3
        )

    documents = (results or {}).get("documents") or []
    chunks = documents[0] if documents else []
    return "\n\n".join(chunks) if chunks else NO_CONTEXT


# --- Routes ------------------------------------------------------------------
@app.post("/api/chat")
async def chat(input: ChatInput):
    """Answer a question with RAG: retrieve context, then ask the LLM."""
    if groq_client is None or chroma_collection is None:
        raise HTTPException(status_code=503, detail="The assistant is unavailable right now.")

    logger.info(
        "chat language=%s message_chars=%d history_items=%d",
        input.language, len(input.message), len(input.history),
    )

    try:
        context_text = await retrieve_context(build_retrieval_query(input.message, input.history))
    except Exception:
        logger.exception("Retrieval failed")
        raise HTTPException(status_code=502, detail="The knowledge base could not be searched. Please try again.")

    system_prompt = (
        f"{get_base_instruction(is_value_question(input.message))}\n"
        f"{get_language_instruction(input.language)}\n\n"
        f"Context:\n{context_text}"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        *build_history_messages(input.history),
        {"role": "user", "content": input.message},
    ]

    try:
        completion = await asyncio.to_thread(
            groq_client.chat.completions.create,
            messages=messages,
            model=LLM_MODEL,
            temperature=0.7,
            max_tokens=200,
            top_p=0.9,
            stream=False,
        )
        answer = completion.choices[0].message.content.strip()
    except Exception:
        logger.exception("LLM request failed")
        raise HTTPException(status_code=502, detail="The language model request failed. Please try again.")

    return {"response": answer, "context": [context_text] if DEBUG_CONTEXT else []}


@app.get("/")
async def root():
    return {"message": "Portfolio Backend is running!", "status": "healthy"}


@app.get("/health")
async def health_check():
    # Liveness stays "healthy"; the flags show whether dependencies loaded.
    return {
        "status": "healthy",
        "service": "portfolio-backend",
        "knowledge_base": chroma_collection is not None,
        "llm": groq_client is not None,
    }
