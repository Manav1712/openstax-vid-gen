import os
import json
from tqdm import tqdm
from chromadb import PersistentClient
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# Load environment variables (for OpenAI API key)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Paths
CHUNKS_JSON = "sample_physics_cropped_leaf_chunks.json"
CHROMA_DIR = "cache/chroma/"
COLLECTION_NAME = "textbook_chunks"


def main():
    # Load chunks
    with open(CHUNKS_JSON, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # Set up ChromaDB persistent client
    os.makedirs(CHROMA_DIR, exist_ok=True)
    client = PersistentClient(path=CHROMA_DIR, settings=Settings(allow_reset=True))
    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION_NAME)
    collection = client.create_collection(COLLECTION_NAME)


    # Set up OpenAI embedding function
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name="text-embedding-3-small"
    )


    # Prepare data for ChromaDB
    ids = []
    documents = []
    metadatas = []
    for i, chunk in enumerate(chunks):
        ids.append(f"chunk_{i}")
        documents.append(chunk["text"])
        # Store all metadata except text
        meta = {k: v for k, v in chunk.items() if k != "text"}
        metadatas.append(meta)


    # Embed and add to ChromaDB in batches
    BATCH_SIZE = 32
    for start in tqdm(range(0, len(documents), BATCH_SIZE), desc="Embedding chunks"):
        end = min(start + BATCH_SIZE, len(documents))
        batch_ids = ids[start:end]
        batch_docs = documents[start:end]
        batch_metas = metadatas[start:end]
        # Compute embeddings for the batch
        batch_embeddings = openai_ef(batch_docs)
        collection.add(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_metas,
            embeddings=batch_embeddings
        )

    print(f"Embedded and indexed {len(documents)} chunks in ChromaDB at {CHROMA_DIR}")

if __name__ == "__main__":
    main() 