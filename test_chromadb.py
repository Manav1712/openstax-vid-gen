from chromadb import PersistentClient
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

CHROMA_DIR = "cache/chroma/"
COLLECTION_NAME = "textbook_chunks"

def inspect_chromadb():
    client = PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(COLLECTION_NAME)
    
    # Set up the same OpenAI embedding function used during indexing
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name="text-embedding-3-small"
    )
    
    print("=== ChromaDB Collection Inspection ===")
    print(f"Total chunks in collection: {collection.count()}")
    print()
    
    # Fetch a few entries (including embeddings)
    results = collection.get(limit=3, include=['embeddings', 'documents', 'metadatas'])
    print("Sample Chunks from ChromaDB:")
    for i in range(len(results['ids'])):
        print(f"ID: {results['ids'][i]}")
        print(f"Metadata: {results['metadatas'][i]}")
        if results['embeddings'] is not None and len(results['embeddings']) > i:
            print(f"Embedding length: {len(results['embeddings'][i])}")
        else:
            print("Embedding: Not retrieved")
        print(f"Text (truncated): {results['documents'][i][:100]}...")
        print("-" * 50)
    
    # Test a simple query using the same embedding function
    print("\n=== Testing Query ===")
    query = "What are significant figures?"
    # Manually embed the query using the same OpenAI function
    query_embedding = openai_ef([query])[0]
    query_results = collection.query(query_embeddings=[query_embedding], n_results=3)
    print(f"Query: '{query}'")
    print("Top 3 results:")
    for i, (doc, meta) in enumerate(zip(query_results['documents'][0], query_results['metadatas'][0])):
        print(f"\nResult {i+1}:")
        print(f"Metadata: {meta}")
        print(f"Text: {doc[:150]}...")
        print("-" * 30)

if __name__ == "__main__":
    inspect_chromadb() 