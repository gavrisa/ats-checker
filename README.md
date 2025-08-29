# ATS Checker — 1‑Day MVP

A lightweight, transparent ATS-style checker you can run locally.

## Features
- Upload **Resume** (PDF/DOCX/TXT) + **Job Description** (paste or file).
- **Match score** = 70% keyword coverage + 30% TF‑IDF cosine similarity.
- Shows **present** vs **missing** JD keywords and suggests **bullet ideas**.
- Detects common **resume sections** (Experience, Skills, Education…).
- Download a **Markdown report**.

> No external APIs. No NLP heavy deps. Clear heuristics.

## Quickstart

```bash
# 1) Create & activate venv (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install
pip install -r requirements.txt

# 3) Run
streamlit run app.py
```

The app opens in your browser (usually http://localhost:8501).

## Notes & Limitations
- PDF parsing uses PyPDF2 (no OCR). If your PDF is scanned images, convert to text first.
- Keyword extraction is frequency-based with a tiny stopword list.
- No synonyms/lemmatization yet (keeps it fast and explainable).
- Cosine similarity via scikit‑learn TF‑IDF on JD+resume pair.
- Intended for **fast iteration** and **clear, developer-friendly logic**.

## Roadmap (nice-to-haves)
- Lemmatization + synonyms (e.g., spaCy or wordnet).
- Phrase-level skills (bi‑grams) and skill ontologies.
- Section-weighted scoring (Experience > Summary > Other).
- Multi-language stopwords.
- Export to PDF report.