# Personal Portfolio Website with AI Chatbot

This repository contains my personal portfolio website, featuring a React frontend, a Python FastAPI backend, and an AI-powered chatbot. The chatbot uses Retrieval-Augmented Generation (RAG) to answer questions about my professional background, drawing from my CV/resume documents.

## 🏗️ Architecture & Key Features

### 🧠 AI Chatbot (RAG)
*   **Knowledge Base**: My CV/resume documents (PDF, DOCX) are processed offline.
*   **Embedding**: Text chunks are converted to numerical vectors using the `sentence-transformers/all-MiniLM-L6-v2` model.
*   **Storage**: Embeddings are stored in a ChromaDB vector database (`backend/.chroma_db`).
*   **Retrieval**: When a user asks a question, it's embedded, and ChromaDB finds the most relevant text chunks.
*   **Generation**: The retrieved context is sent to the Groq API (Llama 3.1) to generate a concise, professional answer.

### 🖥️ Frontend (React & Tailwind CSS)
*   Responsive, single-page application (SPA) located in the `frontend/` directory.
*   Interactive UI components showcasing projects, skills, and experience.
*   Integrated chatbot interface with typing indicators and message history.
*   Auto-play policy compliant background music.

### ⚙️ Backend (FastAPI & Python)
*   RESTful API for chat interactions and health checks.
*   Rate limiting (IP-based) to prevent API abuse.
*   Manages the ChromaDB collection for RAG.

### 🧮 Dedicated Embedding API (FastAPI & Python)
*   A separate service to handle the computationally intensive task of generating text embeddings.
*   Loads the embedding model (`all-MiniLM-L6-v2`) from local disk to avoid runtime downloads and SSL issues.
*   Designed for deployment on Render's free tier (512MB RAM) by offloading memory usage from the main backend.
*   Ensures stability and performance of the main website backend.

### ☁️ Deployment
*   **Frontend**: Deployed on GitHub Pages using GitHub Actions.
*   **Backend & Embedding API**: Deployed on Render (Free Tier).
*   **Database**: ChromaDB index is persisted and committed to the repository via Git LFS.

## 🚀 Getting Started

### Prerequisites
*   Node.js & Yarn (for frontend)
*   Python 3.9+ & `pip` (for backend services)
*   Git & Git LFS (for managing large model/database files)

### Cloning the Repository
```bash
git clone https://github.com/mushtaq96/portfolio-react-app.git
cd portfolio-react-app
```

### Frontend Setup & Local Development
1.  Navigate to the frontend directory: `cd frontend`
2.  Install dependencies: `yarn install`
3.  Start the development server: `yarn start`
4.  Open [http://localhost:3000](http://localhost:3000) in your browser.

### Backend Setup & Local Development

#### 1. Main Backend (`backend/`)
*   **Virtual Environment**: Create and activate a virtual environment (e.g., `python -m venv .venv && source .venv/bin/activate`).
*   **Dependencies**: Install required packages: `pip install -r backend/requirements.txt`.
*   **Environment Variables**:
    *   Create a `.env` file in the `backend/` directory.
    *   Add `GROQ_API_KEY=your_actual_groq_api_key_here`.
    *   *(Optional for local dev)* Add `EMBEDDING_API_URL=http://localhost:8001` (if running the Embedding API locally).
*   **Run**: `cd backend && uvicorn main:app --reload --port 8000`.

#### 2. Embedding API (`embedding_api/`)
*   **Virtual Environment**: Create and activate a virtual environment (e.g., `python -m venv .venv_embedding_api && source .venv_embedding_api/bin/activate`).
*   **Dependencies**: Install required packages: `pip install -r embedding_api/requirements.txt`.
*   **Model**: The `sentence-transformers/all-MiniLM-L6-v2` model is stored locally in `embedding_api/local_models/` and tracked with Git LFS.
*   **Run**: `cd embedding_api && uvicorn main:app --reload --port 8001`.

### Data Preparation (Offline)
1.  Place your CV/resume documents (PDF, DOCX) in `backend/.documents/English/` and `backend/.documents/German/`.
2.  Activate the backend virtual environment.
3.  Run the build script: `cd backend && python build.py`. This script processes the documents, generates embeddings using the model specified in `document_processor.py` (which should match the Embedding API model), and creates/updates the `backend/.chroma_db/` folder.

## 🧪 Testing the AI Chatbot

You can test the chatbot via the frontend UI or directly using `curl`:

```bash
curl -X POST http://localhost:8000/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "What are your key technical skills?", "language": "en"}'
```

Try these example prompts:
*   English: "What value do you bring to address current IT shortages?", "Tell me about your cloud experience."
*   German: "Welchen Mehrwert bieten Sie bei aktuellen IT-Engpässen?", "Erzählen Sie mir von Ihrer Cloud-Erfahrung."

## 📦 Deployment

### Frontend (GitHub Pages)
1.  Update the `homepage` field in `frontend/package.json` if deploying to a different repo/user.
2.  *(If using a script like `yarn run deploy` from the root)*: Ensure your deployment script (e.g., `gh-pages -d frontend/build`) correctly points to the built files in `frontend/build`.
3.  *(Or using GitHub Actions)*: Update your workflow file (e.g., `.github/workflows/deploy.yml`) to build from the `frontend` directory and publish the `frontend/build` folder:
    ```yaml
    # ... (other workflow steps)
    - name: Build
      run: cd frontend && yarn build # Change: Navigate to frontend

    - name: Deploy
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./frontend/build # Change: Point to frontend build directory
    # ...
    ```

### Backend & Embedding API (Render)
1.  Ensure the `all-MiniLM-L6-v2` model files in `embedding_api/local_models/` and the generated `.chroma_db` folder in `backend/` are committed and pushed to GitHub (they are tracked with Git LFS).
2.  Create two Web Services on Render:
    *   **Main Backend**:
        *   Name: `portfolio-backend`
        *   Root Directory: `backend`
        *   Build Command: `pip install -r requirements.txt`
        *   Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
        *   Environment Variables:
            *   `GROQ_API_KEY`: Your actual Groq API key.
            *   `EMBEDDING_API_URL`: The public URL of your deployed Embedding API service (e.g., `https://your-embedding-api.onrender.com`).
            *   `PORT`: `10000` (or Render's default `$PORT`).
    *   **Embedding API**:
        *   Name: `mushtaq-embedding-api`
        *   Root Directory: `embedding_api`
        *   Build Command: `pip install -r requirements.txt`
        *   Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
        *   Environment Variables:
            *   `EMBEDDING_MODEL_NAME`: `all-MiniLM-L6-v2`
            *   `PORT`: Render's default `$PORT`.

## 🛠️ Technical Decisions & Rationale

### Choosing `all-MiniLM-L6-v2`
*   **Model Characteristics**: This model maps sentences & paragraphs to a **384 dimensional dense vector space**. It was fine-tuned on a large dataset of over 1 billion sentence pairs using contrastive learning. By default, input text longer than 256 word pieces is truncated.
*   **Performance & Efficiency**: This model is significantly smaller (~175MB) than multilingual alternatives like `paraphrase-multilingual-MiniLM-L12-v2` (~900MB), making it ideal for the Embedding API to stay within Render's 512MB RAM limit while providing robust semantic understanding for the RAG pipeline.
*   **Capability**: While trained primarily on English data, its broad training makes it suitable for capturing semantic meaning in other languages like German to a reasonable degree, supporting the bilingual nature of the portfolio.
*   **Reliability**: Loading the model from local disk (via Git LFS) avoids runtime network dependencies and potential SSL issues, ensuring consistent startup and operation on deployment platforms like Render.

### Performance & Efficiency Considerations
*   **Resource Optimization**: The dedicated Embedding API service isolates memory-intensive operations, preventing the main backend from exceeding Render's free tier limits.
*   **Cost Awareness**: Designed specifically for cost-effective deployment on free tiers (Render, GitHub Pages). Monitored Groq API usage via rate limiting helps manage potential costs.
*   **Latency**: *(Optional - Add if you have data)* Typical response time for simple queries is under [X] seconds on the Render free tier.

### Security Considerations
*   **API Key Management**: Groq API keys are stored securely using environment variables on the deployment platform (Render).
*   **Rate Limiting**: IP-based rate limiting is implemented on the `/api/chat` endpoint to prevent abuse of the Groq API and protect backend resources.

---

## 📊 Performance & Metrics *(Estimated on Free Tier)*
*   **Embedding Dimensionality**: 384
*   **Model Size**: ~175 MB
*   **Memory Usage (Embedding API)**: ~400 MB RSS when loaded
*   **Response Latency (Est.)**: Typically under 2 seconds for simple queries (depends on Groq API).

## 📸 Screenshots *(Coming Soon)*
*(Placeholder for screenshots of the frontend UI and a sample chat interaction)*

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚀 Future Work
*   Migrate frontend build process to Vite for faster development and modern tooling.
*   Implement more sophisticated caching mechanisms for common queries.
*   Explore multi-turn conversation capabilities for the chatbot.

---