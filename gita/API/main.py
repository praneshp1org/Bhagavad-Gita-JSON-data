from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
import os
from typing import List, Optional, Dict, Any

# Run the Server 
# uvicorn gita.api.main:app --reload


# --- Configuration ---
# This path logic assumes the script is run from within the project root
# and finds the project root by splitting at the 'gita' directory.
try:
    base_dir = os.path.abspath(os.path.dirname(__file__)).split("gita")[0]
    CHROMA_DB_PATH = os.path.join(base_dir, "gita", "knowledge_base", "gita_knowledge_db")
    COLLECTION_NAME = "gita_knowledge"
except IndexError:
    raise RuntimeError("Could not determine the project's base directory. Make sure the 'gita' directory is in the path.")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Bhagavad Gita Q&A API",
    description="An API to query a ChromaDB vector store of the Bhagavad Gita.",
    version="1.0.0",
)

# --- Pydantic Models for API I/O ---
class QueryRequest(BaseModel):
    query: str
    n_results: int = 3
    page_filter: Optional[int] = None

class QueryResult(BaseModel):
    context: str
    page: int
    distance: float

class QueryResponse(BaseModel):
    results: List[QueryResult]
    llm_output: str

# --- ChromaDB Client ---
# This is initialized once when the module is loaded.
client = None
collection = None
try:
    if not os.path.exists(CHROMA_DB_PATH):
        raise FileNotFoundError(f"ChromaDB path not found: {CHROMA_DB_PATH}. Please run create_vector_store.py first.")
    
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)
    print(f"Successfully connected to ChromaDB and loaded collection '{COLLECTION_NAME}'.")
except Exception as e:
    print(f"FATAL: Could not connect to ChromaDB or get collection. {e}")

# --- API Endpoints ---
@app.post("/query", response_model=QueryResponse, summary="Query the Gita")
def query_gita(request: QueryRequest) -> QueryResponse:
    """
    Query the Bhagavad Gita vector store to find relevant passages.

    - **query**: The question or text to search for.
    - **n_results**: The number of results to return.
    - **page_filter**: (Optional) An integer to filter results by a specific page number.
    """
    if not collection:
        raise HTTPException(
            status_code=503, 
            detail="Database connection not available. Ensure the vector store has been created."
        )

    query_params: Dict[str, Any] = {
        "query_texts": [request.query],
        "n_results": request.n_results,
    }

    if request.page_filter is not None and request.page_filter > 0:
        query_params["where"] = {"page": request.page_filter}

    try:
        results = collection.query(**query_params)
        
        response_results = []
        if results and results['ids'] and results['ids'][0]:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]
                response_results.append(
                    QueryResult(
                        context=doc,
                        page=metadata.get('page', -1),
                        distance=distance
                    )
                )
        
        # Placeholder for future LLM integration.
        # This is where you would take the `response_results` (context) and the
        # original `request.query` to generate a response from a Large Language Model.
        # For now, we'll just return a static message.
        llm_response_placeholder = f"This is a placeholder for the LLM's response to the query: '{request.query}'"

        return QueryResponse(results=response_results, llm_output=llm_response_placeholder)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during the query: {str(e)}")

@app.get("/", summary="Root Endpoint", include_in_schema=False)
def read_root():
    """
    A welcome message for the API.
    """
    return {"message": "Welcome to the Bhagavad Gita API. Visit /docs for API documentation."}