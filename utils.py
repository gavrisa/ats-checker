import io, re
from typing import List, Tuple, Set
from collections import Counter
import math

# Очень лёгкий стоплист
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
    text = re.sub(r"[^a-z0-9+.#/ ]+", " ", text)  # оставим + . # / как полезные символы
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize(text: str) -> List[str]:
    return [t for t in text.split() if t not in STOPWORDS and len(t) > 2]

def top_keywords(text: str, top_n: int = 30) -> List[str]:
    tokens = tokenize(text)
    freq = Counter(tokens)
    common = [w for w, _ in freq.most_common(top_n*2)]
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

# --- без sklearn: минимальный TF-IDF и косинус ---
def _tf(tokens: List[str]) -> Counter:
    return Counter(tokens)

def _idf(vocab: List[str], docs: List[List[str]]) -> dict:
    N = len(docs)
    df = {w: 0 for w in vocab}
    for w in vocab:
        for d in docs:
            if w in set(d):
                df[w] += 1
    idf = {w: math.log((N + 1) / (df[w] + 1)) + 1.0 for w in vocab}
    return idf

def _vec(tokens: List[str], vocab: List[str], idf: dict) -> List[float]:
    tf = _tf(tokens)
    vec = []
    for w in vocab:
        vec.append((tf.get(w, 0)) * idf[w])
    return vec

def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

def compute_similarity(jd_text: str, resume_text: str) -> float:
    # токены
    t1 = tokenize(jd_text)
    t2 = tokenize(resume_text)
    vocab = sorted(list(set(t1) | set(t2)))
    if not vocab:
        return 0.0
    idf = _idf(vocab, [t1, t2])
    v1 = _vec(t1, vocab, idf)
    v2 = _vec(t2, vocab, idf)
    return float(_cosine(v1, v2))

def suggest_missing_keywords(keywords: List[str], resume_text: str, top_k_show: int = 12) -> Tuple[List[str], List[str], float]:
    rtokens = set(tokenize(resume_text))
    present = [k for k in keywords if k in rtokens]
    missing = [k for k in keywords if k not in rtokens]
    coverage = (len(present) / max(1, len(keywords)))
    return present, missing[:top_k_show], coverage

def detect_sections(text_raw: str) -> Set[str]:
    found = set()
    lines = [l.strip().lower() for l in text_raw.splitlines() if l.strip()]
    blob = "\n".join(lines)
    for s in SECTION_HINTS:
        pattern = r"(?:^|[\n\r\t ])" + re.escape(s) + r"(?:\s*[:\-]|$)"
        if re.search(pattern, blob, flags=re.IGNORECASE):
            found.add(s.lower())
    return found
