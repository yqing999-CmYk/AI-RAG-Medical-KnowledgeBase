import chunk
import chromadb
from google import genai
import os

google_client = genai.Client() # The client automatically picks up the GEMINI_API_KEY environment variable
EMBEDDING_MODEL = "gemini-embedding-exp-03-07"
LLM_MODEL = "gemini-2.0-flash-lite"  #"gemini-1.5-flash-latest"

chromadb_client = chromadb.PersistentClient("./chroma.db")
chromadb_collection = chromadb_client.get_or_create_collection("childhoodcancer")

def embed(text: str, store: bool) -> list[float]:
    result = google_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config={
            "task_type": "RETRIEVAL_DOCUMENT" if store else "RETRIEVAL_QUERY"
        }
    )

    assert result.embeddings
    assert result.embeddings[0].values
    return result.embeddings[0].values

def create_db() -> None:
    for idx, c in enumerate(chunk.get_chunks()):
        print(f"Process: {c}")
        embedding = embed(c, store=True)
        chromadb_collection.upsert(
            ids=str(idx),
            documents=c,
            embeddings=embedding
        )

def query_db(question: str) -> list[str]:
    question_embedding = embed(question, store=False)
    result = chromadb_collection.query(
        query_embeddings=question_embedding,
        n_results=5
    )
    assert result["documents"]
    return result["documents"][0]


if __name__ == '__main__':
    # Verify API key is set
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: No GOOGLE_API_KEY or GEMINI_API_KEY found in environment")
    else:
        print(f"API key found: {api_key[:8]}...")

    create_db()

    question = "Has some new method been proposed to treat childhood cancer?"
    chunks = query_db(question)
    prompt = "Please answer user's question according to context\n"
    prompt += f"Question: {question}\n"
    prompt += "Context:\n"
    for c in chunks:
        prompt += f"{c}\n"
        prompt += "-------------\n"

    # Use gemini-1.5-flash to generate response based on the retrieved context
    result = google_client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt
    )
    # Print the actual text response, instead of the full response object print(result)
    print(result.text)
   


