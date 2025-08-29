
import io, re
from typing import List, Tuple, Set
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

# Very small stopword list to keep things lightweight
STOPWORDS = set("""a an the and or if when to of for with on in into over under from by at as is are was were be been being do does did doing has have had having this that these those your you we they he she it our their not no yes but so than then too very more most such only own same other """.split())

SECTION_HINTS = [
    "experience", "work experience", "skills", "education", "projects", "summary", "about", "profile",
    "achievements", "interests", "portfolio", "links", "certifications", "awards"
]

def _read_pdf(file) -> str:
    try:
        import PyPDF2
    except Exception:
        return ""
    try:
        reader = PyPDF2.PdfReader(file)
        texts = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")
        return "\n".join(texts)
    except Exception:
        return ""

def _read_docx(file) -> str:
    try:
        from docx import Document
    except Exception:
        return ""
    try:
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception:
        return ""

def extract_text_from_file(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    data = uploaded_file.read()
    # Reset pointer for libraries that expect file-like object
    bio = io.BytesIO(data)
    if name.endswith(".pdf"):
        return _read_pdf(bio) or data.decode("utf-8", errors="ignore")
    elif name.endswith(".docx"):
        return _read_docx(bio) or data.decode("utf-8", errors="ignore")
    else:
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return ""

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+.#/ ]+", " ", text)  # keep some symbols like + . # /
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize(text: str) -> List[str]:
    return [t for t in text.split() if t not in STOPWORDS and len(t) > 2]

def top_keywords(text: str, top_n: int = 30) -> List[str]:
    tokens = tokenize(text)
    freq = Counter(tokens)
    common = [w for w, _ in freq.most_common(top_n*2)]  # take more, then filter
    # simple filter: drop purely numeric tokens and duplicates
    filtered = []
    for w in common:
        if w.isdigit():
            continue
        if w in filtered:
            continue
        filtered.append(w)
        if len(filtered) >= top_n:
            break
    return filtered

def compute_similarity(jd_text: str, resume_text: str) -> float:
    try:
        vec = TfidfVectorizer(stop_words="english", min_df=1)
        X = vec.fit_transform([jd_text, resume_text])
        from sklearn.metrics.pairwise import cosine_similarity
        sim = cosine_similarity(X[0], X[1])[0][0]
        return float(sim)
    except Exception:
        return 0.0

def suggest_missing_keywords(keywords: List[str], resume_text: str, top_k_show: int = 12) -> Tuple[List[str], List[str], float]:
    rtokens = set(tokenize(resume_text))
    present = [k for k in keywords if k in rtokens]
    missing = [k for k in keywords if k not in rtokens]
    coverage = (len(present) / max(1, len(keywords)))
    return present, missing[:top_k_show], coverage

def detect_sections(text_raw: str) -> Set[str]:
    found = set()
    # simple: look for section words as standalone lines or followed by newline/colon
    lines = [l.strip().lower() for l in text_raw.splitlines() if l.strip()]
    blob = "\n".join(lines)
    for s in SECTION_HINTS:
        pattern = r"(?:^|[\n\r\t ])" + re.escape(s) + r"(?:\s*[:\-]|$)"
        if re.search(pattern, blob, flags=re.IGNORECASE):
            found.add(s.lower())
    return found
