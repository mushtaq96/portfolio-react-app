# Argusa AI Challenge 2025 – RAG System

**Author**: SM Mushtaq Bokhari  
**Goal**: Answer 26+ questions from a complex multimodal dataset using a stateless, cost-efficient RAG pipeline (~€2/month).

---

## 📁 Project Structure

```
/backend
├── main.py                 # FastAPI app: /api/chat, /api/batch-qa, /api/index-documents
├── document_processor.py   # Unified parser for 17+ file types (PDF, DOCX, PPTX, EML, CSV, JSON, ZIP, images via OCR, etc.)
├── prompts.py              # Strict instruction prompt for grounded, formatted answers
├── processed_files.json    # Tracks indexed files (mtime-based incremental loading)
├── .chroma_db/             # Persistent ChromaDB vector store (embeddings: all-MiniLM-L6-v2)
├── Material_GreenHorizon/  # Raw challenge dataset (do not modify)
└── submission.json         # Output of /api/batch-qa in required JSON format
```

---

## ⚙️ Key Components

### 1. **Ingestion**

- Run `ALLOW_INDEXING=true uvicorn main:app` → enables `/api/index-documents`
- Processes all files in `Material_GreenHorizon/` recursively
- Skips already-processed files using `processed_files.json`
- Chunks text (1000 chars), stores `source_doc`, `file_path`, and full text in ChromaDB

### 2. **Retrieval**

- **Pure semantic search** (ChromaDB + `all-MiniLM-L6-v2`)
- ❌ **Hybrid search attempted but disabled** — `$contains` not supported in ChromaDB metadata filters
- Uses `n_results=7` (increased for broader context)
- Retrieves chunks + metadata for source tracing

### 3. **Generation**

- **LLM**: Groq (`llama-3.1-8b-instant`)
- **Prompt**: Strictly enforces:
  - No hallucination
  - Project lists with colons
  - Email answers as `(filename in folder)`
  - Role synthesis from multiple chunks
- Output format: `{ "participant_id": "...", "answers": [{ "question_id": "Q1", "answer": "..." }] }`

---

## 🚀 Usage

### Index documents (one-time or incremental)

```bash
export ALLOW_INDEXING=true
uvicorn main:app --port 8000
# Then POST to http://localhost:8000/api/index-documents
```

### Generate submission

```bash
curl -X POST http://localhost:8000/api/batch-qa
# Output saved to submission.json
```

### Chat interactively

```bash
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"message":"What is EcoFlex?"}'
```

---

## 🔧 Known Issues & Notes

- **Hybrid search failed** due to ChromaDB’s lack of `$contains` support → reverted to semantic-only with high `n_results`
- **Q1/Q3/Q6/Q7/Q11/Q12/Q13/Q25** may be incomplete due to retrieval gaps (not prompt)
- **Do not delete `.chroma_db/`** — rebuilding takes time
- To improve answers:
  1. Increase `n_results` in `process_rag_query`
  2. Add metadata keywords during ingestion (e.g., `"project": "aquasentinel"`)
  3. Use a BM25 fallback retriever alongside ChromaDB

---

## 💡 Future Ideas

- Replace ChromaDB with **LanceDB** or **Qdrant** for proper hybrid search
- Add **re-ranking** (e.g., Cohere Rerank or open-source cross-encoder)
- Cache Groq responses during dev to save credits

> **Remember**: The system is only as good as the retrieved context. If the right file isn’t in the top 7 chunks, the answer will be wrong — no matter how good the prompt is. Focus on retrieval first.

Based on the analysis of your current system's behavior with `n_results=7`, here are several alternative approaches to improve retrieval precision:

### 1. Query Enhancement Strategies

- Implement query expansion by generating multiple related queries 4:0
- Use LLMs to create semantically similar queries that cover different aspects of the topic
- Example implementation:

```python
# Generate multiple related queries
queries = [original_query] + augmented_queries
results = collection.query(query_texts=queries, n_results=5)
```

### 2. Cross-Encoder Reranking

- Implement a cross-encoder to rerank retrieved documents based on their semantic relevance 4:1
- Use models like `cross-encoder/ms-marco-MiniLM-L-6-v2` for more accurate relevance scoring
- Example implementation:

```python
from sentence_transformers import CrossEncoder
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
pairs = [[query, doc] for doc in retrieved_documents]
scores = cross_encoder.predict(pairs)
```

### 3. Advanced Embedding Functions

- Use specialized embedding models like `multilingual-e5-large` for better semantic understanding 2:1
- Implement custom embedding functions with domain-specific models
- Example implementation:

```python
from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained('intfloat/multilingual-e5-large')
model = AutoModel.from_pretrained('intfloat/multilingual-e5-large')
```

### 4. Metadata-Based Filtering

- Implement metadata filtering to restrict searches to relevant document types 5:9
- Use document attributes like source, date, or topic to narrow down results
- Example implementation:

```python
results = collection.query(
    query_texts=[query],
    where={"topic": "relevant_topic"}  # filter by metadata
)
```

### 5. Custom Chunking Strategies

- Implement semantic-aware chunking to better handle document segmentation 3:0
- Use techniques like `ClusterSemanticChunker` for more effective document partitioning
- Focus on maintaining semantic coherence within chunks

### 6. Hybrid Search Approach

- Combine multiple retrieval strategies for better results 4:0
- Implement query expansion with cross-encoder reranking
- Use metadata filtering to constrain the search space

These approaches address the core issues in your current system where increasing `n_results` alone hasn't provided sufficient improvement. By implementing these strategies, you can improve retrieval precision without relying solely on increasing the number of results returned.
