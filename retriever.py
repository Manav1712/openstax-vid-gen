import os
import json
from typing import List, Dict, Optional
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Paths
CHROMA_DIR = "cache/chroma/"
COLLECTION_NAME = "textbook_chunks"

class HybridRetriever:
    def __init__(self):
        self.client = PersistentClient(path=CHROMA_DIR)
        self.collection = self.client.get_collection(COLLECTION_NAME)
        
        # Set up OpenAI embedding function
        self.openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=OPENAI_API_KEY,
            model_name="text-embedding-3-small"
        )
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Perform hybrid search using similarity search and MMR diversity.
        
        Args:
            query: User's search query
            top_k: Number of results to return
            
        Returns:
            List of dictionaries containing chunk information
        """
        # Check if query seems to be asking for a specific section
        metadata_filter = self._parse_metadata_query(query)
        
        if metadata_filter:
            return self._metadata_filtered_search(query, metadata_filter, top_k)
        else:
            return self._direct_similarity_search(query, top_k)
    
    def _parse_metadata_query(self, query: str) -> Optional[Dict]:
        """
        Simple metadata parsing for common patterns.
        """
        query_lower = query.lower()
        
        # Look for section patterns like "1.1", "section 1.2", etc.
        import re
        section_match = re.search(r'(?:section\s*)?(\d+\.\d+)', query_lower)
        if section_match:
            return {"section": section_match.group(1)}
        
        # Look for chapter patterns
        chapter_match = re.search(r'chapter\s*(\d+)', query_lower)
        if chapter_match:
            return {"chapter": int(chapter_match.group(1))}
        
        return None
    
    def _metadata_filtered_search(self, query: str, metadata_filter: Dict, top_k: int) -> List[Dict]:
        """
        Search with metadata filtering.
        """
        # Get all chunks first
        all_results = self.collection.get(include=['documents', 'metadatas'])
        
        # Filter by metadata
        filtered_chunks = []
        for i, metadata in enumerate(all_results['metadatas']):
            match = True
            for key, value in metadata_filter.items():
                if key not in metadata or metadata[key] != value:
                    match = False
                    break
            
            if match:
                filtered_chunks.append({
                    'text': all_results['documents'][i],
                    'metadata': metadata,
                    'score': 0.0  # Will be computed by similarity
                })
        
        if not filtered_chunks:
            # Fall back to regular search if no metadata matches
            return self._direct_similarity_search(query, top_k)
        
        # Rank filtered chunks by similarity
        return self._rank_by_similarity(query, filtered_chunks, top_k)
    
    def _rank_by_similarity(self, query: str, chunks: List[Dict], top_k: int) -> List[Dict]:
        """
        Rank chunks by similarity to query.
        """
        query_embedding = self.openai_ef([query])[0]
        
        # Get embeddings for all chunks
        chunk_texts = [chunk['text'] for chunk in chunks]
        chunk_embeddings = self.openai_ef(chunk_texts)
        
        # Calculate similarities
        for i, chunk in enumerate(chunks):
            # Simple dot product similarity (cosine similarity for normalized vectors)
            similarity = np.dot(query_embedding, chunk_embeddings[i])
            chunk['score'] = 1 - similarity  # Convert to distance-like score
        
        # Sort by similarity and apply MMR
        chunks.sort(key=lambda x: x['score'])
        return self._mmr_diversity(chunks, top_k)
    
    def _direct_similarity_search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Direct similarity search using ChromaDB.
        """
        # Embed the query
        query_embedding = self.openai_ef([query])[0]
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k * 2, 10)  # Get more results for MMR
        )
        
        # Convert to our format
        chunks = []
        for i in range(len(results['documents'][0])):
            chunks.append({
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'score': results['distances'][0][i] if 'distances' in results else 1.0
            })
        
        # Apply MMR for diversity
        return self._mmr_diversity(chunks, top_k)
    
    def _mmr_diversity(self, chunks: List[Dict], top_k: int, lambda_param: float = 0.5) -> List[Dict]:
        """
        Apply Maximal Marginal Relevance for diversity.
        
        Args:
            chunks: List of chunk dictionaries
            top_k: Number of results to return
            lambda_param: Balance between relevance (0) and diversity (1)
        """
        if len(chunks) <= top_k:
            return chunks
        
        # Start with the most relevant chunk
        selected = [chunks[0]]
        remaining = chunks[1:]
        
        while len(selected) < top_k and remaining:
            # Calculate MMR scores
            mmr_scores = []
            for chunk in remaining:
                # Relevance score (inverse of distance)
                relevance = 1 - chunk['score']
                
                # Diversity score (minimum similarity to selected chunks)
                diversity = 1.0
                if selected:
                    similarities = []
                    for selected_chunk in selected:
                        # Simple similarity based on text overlap
                        similarity = self._text_similarity(chunk['text'], selected_chunk['text'])
                        similarities.append(similarity)
                    diversity = 1 - max(similarities)
                
                # MMR score
                mmr_score = lambda_param * relevance + (1 - lambda_param) * diversity
                mmr_scores.append(mmr_score)
            
            # Select chunk with highest MMR score
            best_idx = np.argmax(mmr_scores)
            selected.append(remaining[best_idx])
            remaining.pop(best_idx)
        
        return selected
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        Simple text similarity based on word overlap.
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0


def test_retriever():
    """
    Test function for the hybrid retriever.
    """
    print("=== Testing Hybrid Retriever ===")
    
    retriever = HybridRetriever()
    
    # Test queries
    test_queries = [
        "What are significant figures?",
        "Explain physical quantities and units",
        "How do we measure accuracy and precision?",
        "What is section 1.1 about?",
        "Tell me about chapter 1"
    ]
    
    for query in test_queries:
        print(f"\n--- Query: '{query}' ---")
        results = retriever.search(query, top_k=3)
        
        for i, result in enumerate(results):
            print(f"\nResult {i+1}:")
            print(f"Section: {result['metadata'].get('section', 'N/A')}")
            print(f"Title: {result['metadata'].get('title', 'N/A')}")
            print(f"Score: {result['score']:.4f}")
            print(f"Text: {result['text'][:150]}...")
            print("-" * 40)


if __name__ == "__main__":
    test_retriever() 