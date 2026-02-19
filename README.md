# AI RAG Knowledge Base

A Retrieval-Augmented Generation (RAG) application that answers natural language questions using a local knowledge base. Built with Google Gemini AI and ChromaDB, served via a Streamlit web interface.

> **Demo domain:** Childhood cancer research — but the architecture works for any markdown knowledge base.

---

## How It Works

```
data.md  ──►  chunk.py  ──►  embed.py  ──►  chroma.db
                               (build)       (vector store)

User question  ──►  embed.py (query)  ──►  chroma.db  ──►  top-5 chunks
                                                              │
                                                              ▼
                                                    Gemini LLM  ──►  Answer
                                                            
```

1. **Chunking** (`chunk.py`): Reads `data.md` and splits it into semantic chunks using double-newline boundaries, prepending each chunk with its nearest `#` heading for context.
2. **Embedding** (`embed.py`): Calls the Google Gemini Embedding API (`gemini-embedding-001`) to convert each chunk into a 3072-dimensional vector, then stores it in ChromaDB.
3. **Querying** (`embed.py → query_db`): Embeds the user's question with the same model and retrieves the 5 most similar chunks via cosine similarity.
4. **Generation** (`embed.py → app.py`): Builds a prompt with the retrieved context and sends it to `gemini-2.5-flash-lite` for a grounded answer.
5. **UI** (`app.py`): Streamlit web interface where the user types a question and sees the answer plus the source chunks.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Package manager | [uv](https://github.com/astral-sh/uv) |
| Embedding model | `gemini-embedding-001` (Google Gemini API) |
| LLM | `gemini-2.5-flash-lite` (Google Gemini API) |
| Vector database | [ChromaDB](https://www.trychroma.com/) (local persistent) |
| Web UI | [Streamlit](https://streamlit.io/) |
| AI SDK | [google-genai](https://pypi.org/project/google-genai/) ≥ 1.59 |

---

---

## Prerequisites

- Python 3.12
- [uv](https://github.com/astral-sh/uv) package manager
- A Google Gemini API key — get one free at [aistudio.google.com](https://aistudio.google.com/)

---

## Setup & Run

### 1. Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and set up the environment

```bash
git clone <repo-url>
cd AI-RAG-KnowBase

uv venv --python 3.12
uv sync
```

### 3. Set your API key

```bash
# Linux / macOS
export GOOGLE_API_KEY="your-key-here"

# Windows (PowerShell)
$env:GOOGLE_API_KEY = "your-key-here"

# Or create a .env file (add to .gitignore!)
echo GOOGLE_API_KEY=your-key-here > .env
```

### 4. Build the vector database (first time only, or when data.md changes)

```bash
uv run python embed.py
```

This embeds all chunks from `data.md` into ChromaDB. Takes ~30 seconds.

### 5. Run the web app

```bash
uv run streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Updating the Knowledge Base

To add new content:

1. Edit `data.md` — use `#` headings to mark topics.
2. Rebuild the vector database:
   ```bash
   uv run python embed.py
   ```
   The old collection is automatically deleted and rebuilt.

---

## Deployment

### Option A: Streamlit Community Cloud (free, easiest)

1. Push the repo to GitHub (exclude `.venv/`, `chroma.db/`, and `.env`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo.
3. Set `GOOGLE_API_KEY` in the Streamlit secrets manager.
4. **Important:** ChromaDB is ephemeral on Streamlit Cloud — you must pre-build `chroma.db` and commit it, or switch to a hosted vector DB like Pinecone or Weaviate.

### Option B: Docker

#### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

COPY . .

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "app.py", \
     "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Build and run

```bash
# Build the image
docker build -t ai-rag-knowbase .

# Run (pass your API key)
docker run -p 8501:8501 \
  -e GOOGLE_API_KEY="your-key-here" \
  ai-rag-knowbase
```

Open [http://localhost:8501](http://localhost:8501).

#### Persist the vector database across container restarts

```bash
docker run -p 8501:8501 \
  -e GOOGLE_API_KEY="your-key-here" \
  -v $(pwd)/chroma.db:/app/chroma.db \
  ai-rag-knowbase
```
---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_API_KEY` | Yes | Google Gemini API key |
| `GEMINI_API_KEY` | Yes (alternative) | Alias — either one works |

---
