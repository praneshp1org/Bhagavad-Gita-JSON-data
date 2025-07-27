import json
import chromadb
import os

# --- Configuration ---
base_dir = os.path.abspath(os.path.dirname(__file__)).split("gita")[0]
JSON_FILE_PATH = os.path.join(base_dir,"gita", "parser", "textbook_gita", "json", "gita.json")
CHROMA_DB_PATH = os.path.join(base_dir,"gita", "knowledge_base", "gita_knowledge_db")
COLLECTION_NAME = "gita_knowledge"


def load_documents_from_json(file_path):
    """
    Loads and processes documents from the Gita JSON file.
    Each page's text becomes a document, and its page number becomes metadata.
    """
    documents = []
    metadatas = []
    ids = []

    print(f"Loading data from {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return [], [], []
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not a valid JSON file.")
        return [], [], []

    # The JSON is a list containing one object, which contains the 'pages'
    if not data or 'page' not in data['pages'][0]:
        print("Error: JSON structure is not as expected. Missing 'page' key.")
        return [], [], []

    for page_data in data['pages']:
        page_number = page_data.get('page')
        page_text = page_data.get('md').strip()

        if page_number is not None and page_text:
            # Document: The text content of the page
            documents.append(page_text)
            
            # Metadata Strategy: Store the page number for each document.
            # This allows for powerful, filtered queries later.
            metadatas.append({"page": page_number})
            
            # ID: A unique identifier for the document.
            ids.append(f"page_{page_number}")

    return documents, metadatas, ids

def create_chroma_vector_store():
    """Creates and populates the ChromaDB vector store."""
    documents, metadatas, ids = load_documents_from_json(JSON_FILE_PATH)

    if not documents:
        print("No documents loaded. Aborting vector store creation.")
        return

    print(f"Loaded {len(documents)} documents to be added to the vector store.")

    # 1. Initialize the Chroma client with persistence to save the data to disk.
    print(f"Initializing ChromaDB at '{CHROMA_DB_PATH}'...")
    os.makedirs(CHROMA_DB_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    # 2. Create or get the collection.
    print(f"Creating or getting collection: '{COLLECTION_NAME}'")
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    # 3. Add documents to the collection. ChromaDB handles embedding automatically.
    print("Adding documents to the collection. This may take a moment...")
    collection.add(documents=documents, metadatas=metadatas, ids=ids)

    print("\n--- Vector Store Creation Complete! ---")
    print(f"Total documents in collection: {collection.count()}")

if __name__ == "__main__":
    create_chroma_vector_store()