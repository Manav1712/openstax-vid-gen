

# Automated Textbook Explainer Video Generator – **Revised with Hybrid Semantic Retrieval**

## 150‑Word Executive Summary

Automated Textbook Explainer Video Generator is a one‑day hackathon prototype that converts any OpenStax PDF chapter into a concise, student‑friendly video explanation. A minimalist Streamlit UI lets students select a chapter/section or type a free‑text question. Under the hood: the PDF is parsed into hierarchical chunks, vector‑indexed with embeddings, and searched via a hybrid retriever that returns only the three most relevant leaf chunks. GPT‑4o turns those chunks into a 60‑second instructional script, which D‑ID renders as a talking‑head video. The entire flow runs locally with Python, Streamlit, ChromaDB, and two external APIs (OpenAI, D‑ID). The result is a demo‑ready tool that showcases fast document retrieval, LLM‑powered pedagogy, and automated video generation—all built in under a day.

---

# **Project Roadmap (Revised)**

## Section 0 · Pre‑Hackathon Admin  *20 min*  ✅ **COMPLETED**

1. Collect `OPENAI_API_KEY`, `DID_API_KEY`.
2. Download/crop sample PDF.
3. Install Python 3.11, create venv.
4. Open project folder in Cursor, stash keys locally.

## Section 1 · Repository & Baseline  *15 min*  ✅ **COMPLETED**

Initialize git, `.gitignore`, `README.md`, MIT license, first commit.

## Section 2 · Project Skeleton  *25 min*  ✅ **COMPLETED**

**Current Structure:**
```
openstax-vid-gen/
├── app.py                                    # Streamlit UI placeholder
├── video_maker.py                            # Orchestration placeholder
├── indexer.py                                # Embedding & ChromaDB indexing
├── retriever.py                              # Hybrid search with MMR
├── test_chromadb.py                          # Testing utility
│
├── parsers/
│   ├── pdf_parser.py                         # Hierarchical PDF chunking
│   └── __init__.py
├── llm/
│   ├── explainer.py                          # LLM script generator placeholder
│   └── __init__.py
├── video/
│   ├── did_client.py                         # D-ID API client placeholder
│   └── __init__.py
├── cache/
│   ├── chroma/                               # ChromaDB vector database
│   └── __init__.py
├── requirements.txt                          # Updated dependencies
├── sample_physics_cropped.pdf                # Cropped textbook
├── sample_physics_cropped_leaf_chunks.json   # Generated chunks
├── .env.example
└── …
```

## Section 3 · Environment & Deps  *15 min*  ✅ **COMPLETED**

**Updated `requirements.txt`:**
```
streamlit
pymupdf
langchain
chromadb
tiktoken
openai
requests
python-dotenv
```

## Section 4 · PDF Parsing & Chunking  *50 min*  ✅ **COMPLETED**

**Implementation:** `parsers/pdf_parser.py`
* ✅ Detects section headings using regex patterns (`CHAPTER X`, `X.Y Title`)
* ✅ Splits each section into ~350-token leaf chunks with 20-token overlap using tiktoken
* ✅ Returns list of dicts with metadata: `chapter`, `section`, `title`, `chunk_index`, `text`, `start_page`, `end_page`
* ✅ Outputs JSON file: `sample_physics_cropped_leaf_chunks.json` (218 chunks)
* ✅ **Test:** `python parsers/pdf_parser.py` → generates chunked JSON

## Section 5 · Embedding & Vector Index  *25 min*  ✅ **COMPLETED**

**Implementation:** `indexer.py`
* ✅ Embeds every leaf chunk using OpenAI's `text-embedding-3-small`
* ✅ Stores 1536-dimensional vectors + metadata in local ChromaDB (`cache/chroma/`)
* ✅ Batch processing (32 chunks/batch) with progress bar
* ✅ **Test:** `python indexer.py` → embeds 218 chunks, stores in ChromaDB
* ✅ **Verification:** `python test_chromadb.py` → inspects database and tests queries

## Section 6 · Hybrid Retriever  *45 min*  ✅ **COMPLETED**

**Implementation:** `retriever.py`
* ✅ **Simplified architecture** (no LangChain dependencies due to deprecation issues)
* ✅ **Metadata parsing:** Detects section/chapter queries using regex
* ✅ **Hybrid search:** Combines metadata filtering + cosine similarity
* ✅ **MMR diversity:** Returns top 3 diverse, relevant chunks
* ✅ **Robust fallbacks:** Falls back to similarity search if metadata filtering fails
* ✅ **Test:** `python retriever.py` → tests 5 different query types
* ✅ **Performance:** Correctly handles both content queries ("What are significant figures?") and structural queries ("What is section 1.1 about?")

## Section 7 · LLM Script Generator  *30 min*  **PENDING**

* `llm/explainer.py` – GPT-4o integration to generate scripts from retrieved chunks
* Function signature: `generate_script(chunks: List[Dict]) -> str`
* Prompt engineering for 60-second educational videos

## Section 8 · D‑ID Video API  *30 min*  **PENDING**

* `video/did_client.py` – D-ID API integration
* Function signature: `create_video(script: str) -> str` (returns video URL)
* Caching by script hash to avoid duplicate API calls

## Section 9 · Orchestration Pipeline  *20 min*  **PENDING**

**Updated `video_maker.py`:**
```python
def generate_video(query: str) -> str:
    # 1. Use retriever to get relevant chunks
    chunks = retriever.search(query, top_k=3)
    # 2. Generate script from chunks
    script = explainer.generate_script(chunks)
    # 3. Create video from script
    video_url = did_client.create_video(script)
    return video_url
```

## Section 10 · Streamlit UI  *45 min*  **PENDING**

* Update `app.py` with full UI
* Free-text input box for queries
* Optional chapter/section dropdown
* Video player for results
* Show retrieved chunks/pages for transparency

## Section 11 · Quality of Life  *30 min*  **PENDING**

Logging, token/cost tracker, pre‑commit, enhanced caching.

## Section 12 · Demo Prep & Submission  *45 min*  **PENDING**

Complete README, demo video/GIF, tag release.

---

# **Implementation Status & Changes Made**

## ✅ **Completed Sections (0-6)**

| Section | Status | Key Achievements |
|---------|--------|------------------|
| 0-3 | ✅ Complete | Environment setup, dependencies, project structure |
| 4 | ✅ Complete | **218 chunks** from cropped PDF, hierarchical chunking working |
| 5 | ✅ Complete | **ChromaDB** with 1536-dim embeddings, verified working |
| 6 | ✅ Complete | **Hybrid retriever** with metadata filtering + MMR, tested |

## 🔧 **Key Implementation Changes**

| Original Plan | What Was Actually Built | Reason |
|---------------|------------------------|---------|
| LangChain SelfQueryRetriever | Custom metadata parsing + direct ChromaDB | LangChain deprecation warnings, missing dependencies |
| Complex BM25 + cosine hybrid | Metadata filtering + cosine similarity + MMR | Simpler, more reliable implementation |
| LangChain dependencies | Direct ChromaDB + OpenAI APIs | Fewer dependencies, more stable |

## 📊 **Current Performance Metrics**

* **PDF Processing:** 218 chunks from cropped textbook
* **Embedding Cost:** ~$0.01 for 218 chunks using text-embedding-3-small
* **Retrieval Speed:** <0.5s for query + MMR ranking
* **Accuracy:** Correctly retrieves relevant sections for both content and structural queries

---

## **Next Steps (Sections 7-12)**

The foundation is solid and tested. Ready to implement:
1. **LLM Script Generator** - GPT-4o integration
2. **D-ID Video API** - Video generation
3. **Orchestration** - Connect all components
4. **UI** - Streamlit interface
5. **Polish** - Logging, caching, demo prep

---

### Updated Implementation Notes

* **Embedding cost:** 218 leaf chunks ≈ 65k tokens → ~$0.01 with text-embedding-3-small
* **Runtime latency:** Retrieval < 0.5s; chunk quality verified through testing
* **Architecture:** Simplified but robust - direct API usage instead of complex frameworks
* **Testing:** All components have working test functions for verification

