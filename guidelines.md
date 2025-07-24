

# Automated Textbook Explainer Video Generator – **Revised with Hybrid Semantic Retrieval**

## 150‑Word Executive Summary

Automated Textbook Explainer Video Generator is a one‑day hackathon prototype that converts any OpenStax PDF chapter into a concise, student‑friendly video explanation. A minimalist Streamlit UI lets students select a chapter/section or type a free‑text question. Under the hood: the PDF is parsed into hierarchical chunks, vector‑indexed with embeddings, and searched via a hybrid (keyword + cosine) retriever that returns only the three most relevant leaf chunks (\~3–4 pages). GPT‑4o turns those chunks into a 60‑second instructional script, which D‑ID renders as a talking‑head video. The entire flow runs locally with Python, Streamlit, LangChain, Chroma, and two external APIs (OpenAI, D‑ID). The result is a demo‑ready tool that showcases fast document retrieval, LLM‑powered pedagogy, and automated video generation—all built in under a day.

---

# **Project Roadmap (Revised)**

## Section 0 · Pre‑Hackathon Admin  *20 min*  **(unchanged)**

1. Collect `OPENAI_API_KEY`, `DID_API_KEY`.
2. Download/crop sample PDF.
3. Install Python 3.11, create venv.
4. Open project folder in Cursor, stash keys locally.

## Section 1 · Repository & Baseline  *15 min*  **(unchanged)**

Initialize git, `.gitignore`, `README.md`, MIT license, first commit.

## Section 2 · Project Skeleton  *25 min*  **(updated)**

```
textbook-video-gen/
├── app.py              # Streamlit UI
├── video_maker.py      # Orchestration
├── indexer.py          # NEW – offline embed/chunk builder
├── retriever.py        # NEW – structured + hybrid search
│
├── parsers/
│   └── pdf_parser.py   # hierarchical splitter
├── llm/
│   └── explainer.py
├── video/
│   └── did_client.py
├── cache/              # JSON + Chroma DB
├── requirements.txt
├── .env.example
└── …
```

Commit: `chore: add skeleton with indexer/retriever`.

## Section 3 · Environment & Deps  *15 min*  **(changed)**

Add to `requirements.txt`:

```
streamlit PyMuPDF langchain chromadb tiktoken openai requests python-dotenv
```

`pip install -r requirements.txt` → commit.

## Section 4 · PDF Parsing & Chunking  *50 min*  **(expanded)**

* `parsers/pdf_parser.py` – detect section headings, then leaf‑split to 350‑token chunks with 20‑token overlap. Return list of dicts with metadata.
* Unit‑test on cropped PDF.

## Section 5 · Embedding & Vector Index  *25 min*  **(new)**

* `indexer.py` – embeds every leaf chunk using `text-embedding-3-small`; stores vectors + metadata in local Chroma (`cache/chroma/`). Run once offline.

## Section 6 · Hybrid Retriever  *45 min*  **(new)**

* `retriever.py` – LangChain `SelfQueryRetriever` → metadata filter → hybrid (BM25 ∧ cosine) search → MMR top K = 3.
* Returns list of ≤3 chunk texts.

## Section 7 · LLM Script Generator  *30 min*  **(renumbered)**

* `llm/explainer.py` unchanged but now receives ≤3 chunks or map‑reduced summary.

## Section 8 · D‑ID Video API  *30 min*  **(renumbered)**

No change except caching `result_url` keyed by script hash.

## Section 9 · Orchestration Pipeline  *20 min*  **(updated)**

`video_maker.generate(query_or_ref)`:

1. If explicit chapter/section → direct metadata filter.
2. Else pass free text to `retriever.search()`.
3. Feed returned chunks to `explainer.make_script`.
4. Send script to `did_client.create_video`.

## Section 10 · Streamlit UI  *45 min*  **(slight change)**

* Add a free‑text box *or* chapter/section dropdown.
* Show search progress & fetched pages.

## Section 11 · Quality of Life  *30 min*

Logging, token/cost tracker, pre‑commit, cache.

## Section 12 · Demo Prep & Submission  *45 min*

README, GIF, tag release.

---

# **What Changed vs. Previous Guide**

| Area             | Old                                  | New                                               |
| ---------------- | ------------------------------------ | ------------------------------------------------- |
| **Dependencies** | streamlit, PyMuPDF, openai, requests | **+ langchain, chromadb, tiktoken**               |
| **Skeleton**     | No `indexer.py` / `retriever.py`     | **Added both files**                              |
| **Parsing**      | Single‑level section split           | **Hierarchical split + leaf chunks**              |
| **Retrieval**    | Simple keyword search                | **Self‑Query + hybrid vector/BM25 + MMR (top 3)** |
| **LLM Calls**    | 1 call (script)                      | **2 calls** (router → script)                     |
| **Total Time**   | \~5 h 10 m                           | **\~6 h 40 m** (adds ≈ 1.5 h for RAG)             |

---

### Implementation Notes

* **Embedding cost:** 100 leaf chunks ≈ 30 k tokens → <\$0.01.
* **Runtime latency:** Retrieval < 0.3 s; GPT‑4o & D‑ID unchanged.
* **Fallback:** If router fails to detect metadata, retriever still works via pure semantic search.

