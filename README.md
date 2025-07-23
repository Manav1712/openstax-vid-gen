# Automated Textbook Explainer Video Generator

## Setup Instructions

1. **Clone the repo and create a virtual environment:**
   ```bash
   python3 -m venv vid-env
   source vid-env/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your OpenAI and D-ID API keys:**
   - Copy `.env.example` to `.env` and fill in your keys.

4. **Add your cropped OpenStax PDF:**
   - Place your PDF (e.g., `sample_physics_cropped.pdf`) in the project root or `pdfs/` folder.

5. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## Notes
- This is a local demo. No deployment or upload UI yet.
- Manual testing is sufficient for hackathon/demo purposes.