# query_script.py
import chromadb
import os

# --- Configuration ---
base_dir = os.path.abspath(os.path.dirname(__file__)).split("gita")[0]
CHROMA_DB_PATH = os.path.join(base_dir,"gita/knowledge_base/gita_knowledge_db")
COLLECTION_NAME = "gita_knowledge"

# Connect to the existing database
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_collection(name=COLLECTION_NAME)

# --- Example Queries ---

# 1. General query across the entire book
results = collection.query(
    query_texts=["What is the nature of the soul?"],
    n_results=2
)
print("General Query Results:")
print(results['documents'])

# 2. Filtered query to search only within a specific page
results_page_45 = collection.query(
    query_texts=["What is the nature of the soul?"],
    where={"page": 45}, # This is the metadata filter
    n_results=1
)
print("\nFiltered Query Results (Page 45):")
print(results_page_45['documents'])
