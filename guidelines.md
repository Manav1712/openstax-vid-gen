# Automated Textbook Explainer Video Generator

## 150‑Word Executive Summary

Automated Textbook Explainer Video Generator is a one‑day hackathon prototype that converts any OpenStax PDF chapter into a concise, student‑friendly video explanation on demand. Students launch a bare‑bones Streamlit app, select a chapter‑section, type what confused them, and within 30 seconds receive a 60‑second talking‑head clip. Under the hood: a Python backend parses PDF, finds the relevant section, summarizes it via GPT‑4o, and passes the script to D-ID’s API for instant avatar narration. With just Python, Streamlit, and two APIs, the project showcases document parsing, LLM-powered explainability, and automated video generation in a deployable workflow. The final product is a clean, demo-ready UI that lets any user go from textbook page to custom explainer video in under a minute—ideal for hackathons, education demos, and rapid prototyping.

---

# Project Roadmap and Steps

## Section 0: Pre-Hackathon Admin

1. Gather API credentials for OpenAI and D-ID.
2. Download OpenStax sample PDF (recommend cropping to just 1–2 chapters for speed).
3. Install/confirm Python 3.11 and create a virtual environment with `pyenv` and `venv`.
4. Prepare the project folder for Cursor, saving API keys and PDF locally (not checked in).
5. Optional: Start a `NOTES.md` for links and test ideas.
6. Double-check: API keys, cropped PDF, venv ready, project open in Cursor.

## Section 1: Repository & Baseline

1. Initialize git repo in Cursor workspace.
2. Create `.gitignore` (ignore `.venv/`, `.env`, `*.mp4`, `cache/`, etc.).
3. Add starter `README.md` and `LICENSE` (MIT).
4. Commit baseline scaffold.

## Section 2: Project Skeleton

- Create full folder/file layout:
  - `app.py` (Streamlit UI)
  - `video_maker.py` (orchestration)
  - `parsers/pdf_parser.py`, `llm/explainer.py`, `video/did_client.py`, `cache/`, `requirements.txt`, `.env.example`, `__init__.py` as needed
- Add to git, commit.

## Section 3: Env & Dependencies

- Write `requirements.txt` (streamlit, PyMuPDF, openai, requests, python-dotenv)
- `pip install -r requirements.txt`
- Commit.

## Section 4: PDF Parsing

- Use PyMuPDF to parse only select chapters/pages (not whole PDF)
- Extract sections/chunks, save as JSON for fast lookup.
- Commit tested extraction code.

## Section 5: LLM Script Generator

- GPT-4o prompt template to explain section as a video script.
- Function takes section text, returns script. Add a test.
- Commit.

## Section 6: D-ID Video API

- Function to call D-ID API (1 credit per video).
- Poll for result, return `result_url`.
- Commit.

## Section 7: Orchestration

- One function: parse → script → video (using above modules).
- Commit.

## Section 8: Streamlit UI

- File upload, dropdowns for chapter/section, textbox for question, button to generate video, video player in UI.
- Commit.

## Section 9: Quality of Life

- Add pre-commit hooks, logging, usage/cost tracking, cache for scripts/videos.
- Commit.

## Section 10: Demo Prep

- Full flow tests, demo GIF/video, complete README.
- Commit/tag as demo release.

## Section 11: Submission Checklist

- README, requirements.txt, .env.example, demo video/file.

---

# Implementation Notes and Hackathon Best Practices

- **Chunk, Search, and Summarize**: For large textbooks, always split into logical chunks (chapter/section or 1–2 pages) and store for fast search and retrieval. Use simple keyword or semantic search to find the right chunk and only send that to the LLM.
- **Cropped PDF**: Never process the full 1,700-page Physics 2e during hackathon time. Pre-crop to one or two chapters or parse a specific page range.
- **D-ID Credits**: 1 credit = 1 video; 12 credits = 12 avatar videos (plan and cache usage).
- **LLM Context Window**: Keep context to one chunk/section at a time for speed and reliability. This is standard for industry-scale doc QA systems and hackathons alike.
- **MVP-Friendly UI**: All demo logic runs in Python and Streamlit—focus on the backend/data flow, not on front-end polish.

# Quick Reference: Sample Chunk Search Code

```python
def search_chunks(user_query, chunks):
    # Simple keyword search
    query = user_query.lower()
    for chunk in chunks:
        if query in chunk["title"].lower() or query in chunk["text"].lower():
            return chunk
    # Fallback: first section of specified chapter
    return next(c for c in chunks if c["chapter"] == desired_chapter)
