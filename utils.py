# utils.py
# -*- coding: utf-8 -*-

import re
from collections import Counter
from typing import List, Set, Tuple, Optional

# ---- Текст из файлов ---------------------------------------------------------

def extract_text_from_file(file) -> str:
    """
    Принимает st.file_uploader объект и вытягивает текст из PDF/DOCX/TXT.
    """
    name = (file.name or "").lower()

    # TXT
    if name.endswith(".txt"):
        data = file.read()
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return data.decode("latin-1", errors="ignore")

    # PDF
    if name.endswith(".pdf"):
        try:
            from PyPDF2 import PdfReader
        except Exception:
            return ""
        text_parts: List[str] = []
        try:
            reader = PdfReader(file)
            for page in reader.pages:
                t = page.extract_text() or ""
                if t:
                    text_parts.append(t)
        except Exception:
            pass
        return "\n".join(text_parts)

    # DOCX
    if name.endswith(".docx"):
        try:
            import docx  # python-docx
        except Exception:
            return ""
        try:
            doc = docx.Document(file)
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            return ""

    # fallback
    try:
        data = file.read()
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""

# ---- Нормализация ------------------------------------------------------------

def clean_text(s: str) -> str:
    s = s.replace("\x00", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\r\n?", "\n", s)
    return s.strip()

def tokenize(text: str) -> List[str]:
    return [t for t in re.findall(r"\b\w+\b", text.lower()) if len(t) > 2]

# ---- Эвристики: компании / география / филлеры -------------------------------

COMPANY_SUFFIXES = r"(?:inc|llc|gmbh|ltd|plc|corp|co|sa|ag|oy|kk|pte|pty|s\.?r\.?l\.?|s\.?a\.?s\.?|asa|ab|bv|nv)\b"

FILLER_STOP: Set[str] = set("""
including include includes about across within among between various multiple
customer customers client clients team teams company companies business businesses
join hiring hire role roles position opportunity opportunities responsibilities requirements
will would may can could must should via using use uses used
and or the a an for with of to in on at by from as is are was were be been being
your you we they our their this that these those it its into acrosses
""".split())

# «пушистые» слова (корпоративная вода, общие слова, лишние прилагательные)
FLUFF_STOP: Set[str] = {
    # общие пустые слова
    "real", "meaningful", "believe", "working", "make", "take", "one", "what", "join", "explore",
    "solutions", "solution", "opportunity", "impact", "value", "role", "responsibility",
    "responsibilities", "requirements", "offer", "offers", "needed", "desired", "preferred",
    "skills", "skill", "experience", "experiences", "knowledge", "understanding", "background",
    "ability", "capable", "strong", "excellent", "good", "great", "big",

    # «водяные» глаголы
    "help", "work", "drive", "support", "develop", "improve", "ensure", "deliver",
    "collaborate", "collaboration", "provide", "including", "build", "building", "contribute",

    # функциональные общие
    "team", "teams", "environment", "organization", "organizational", "project", "projects",
    "business", "customers", "client", "clients", "stakeholders", "company", "companies",

    # прилагательные без смысла
    "fast", "innovative", "new", "next", "future", "current", "global", "local",
    "international", "stronger", "better", "best", "leading", "unique", "key", "important",

    # часто «везде и ни о чём»
    "platform", "system", "systems", "process", "processes", "approach", "methods", "tools",
    "culture", "focus", "needs", "goal", "vision", "mission", "strategy", "strategic",

    # ещё немного
    "more", "high", "low", "many", "across", "around", "different", "various",

    # и то, что мешало в твоих тестах
    "service", "services", "sales", "offerings",
}

GEO_STOP: Set[str] = set("""
nordic nordics europe european cet cest oslo helsinki stockholm norway sweden finland
germany france uk britain england denmark iceland scandinavia
""".split())

def _norm_name(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^\w\s.-]", " ", s)
    s = re.sub(rf"\b{COMPANY_SUFFIXES}\.?$", "", s.strip())
    return re.sub(r"[\s._-]+", " ", s).strip()

def detect_company_names(jd_text: str) -> Set[str]:
    """
    Пытаемся найти название компании в JD (без внешних NLP либ, только регексы).
    Возвращаем нормализованные имена + их части потом используем как стоп-слова.
    """
    cand: Set[str] = set()
    text = jd_text.strip()
    lower = text.lower()

    # 1) первые три строки — там часто шапка/бренд
    head = "\n".join(text.splitlines()[:3])
    caps = re.findall(
        r"\b([A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){0,2})(?:\s+" + COMPANY_SUFFIXES + r")?\b",
        head
    )
    for s in caps:
        cand.add(_norm_name(s))

    # 2) шаблоны 'at X', 'About X', 'Join X', 'We at X'
    for m in re.findall(r"\b(?:at|about|join|we at)\s+([A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){0,2})", text):
        cand.add(_norm_name(m))

    # 3) 'X is hiring/looking…'
    for m in re.findall(r"\b([A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){0,2})\s+(?:is|are)\s+(?:hiring|looking)", text):
        cand.add(_norm_name(m))

    # 4) домены в ссылках/почте → базовое имя
    for dom in re.findall(r"https?://(?:www\.)?([a-z0-9-]+)\.(?:com|io|ai|co|tech|net|org|no|se|fi|uk|de|fr)\b", lower):
        cand.add(_norm_name(dom))
    for dom in re.findall(r"\b[a-z0-9._%+-]+@([a-z0-9-]+)\.(?:com|io|ai|co|tech|net|org|no|se|fi|uk|de|fr)\b", lower):
        cand.add(_norm_name(dom))

    cand -= {"careers", "jobs", "hiring", "company"}
    return {c for c in cand if c}

# ---- Ключевые слова -----------------------------------------------------------

def top_keywords(jd_text: str, top_n: int = 30) -> List[str]:
    """
    Извлекает ключевые слова из JD:
    - игнорирует название компании (и его части);
    - игнорирует географию и «пушистые»/филлерные слова;
    - даёт частотную выборку с небольшим оверфетчем.
    """
    tokens = tokenize(jd_text)
    companies = detect_company_names(jd_text)

    company_parts: Set[str] = set()
    for c in companies:
        company_parts.add(c)
        company_parts.update(c.split())

    stop = FILLER_STOP | FLUFF_STOP | GEO_STOP | company_parts

    freq = Counter(tokens)
    result: List[str] = []
    for w, _cnt in freq.most_common(top_n * 5):  # небольшой запас
        if not w or w.isdigit():
            continue
        if w in stop:
            continue
        result.append(w)
        if len(result) >= top_n:
            break

    # финальная страховка от попадания «компании» в выдачу
    result = [w for w in result if w not in companies and w not in company_parts]
    return result

# ---- (опционально) простой скоринг совпадений --------------------------------

def compute_keyword_overlap(resume_tokens: List[str], jd_keywords: List[str]) -> Tuple[int, int, float]:
    """
    Возвращает (пересечение, всего JD-ключей, процент).
    """
    rset = set(resume_tokens)
    jset = set(jd_keywords)
    inter = len(rset & jset)
    total = max(1, len(jset))
    score = round(100.0 * inter / total, 1)
    return inter, total, score
# --- простая метрика схожести без sklearn (0..100) ---
from typing import Iterable

def compute_similarity(resume_kw: Iterable[str], jd_kw: Iterable[str]) -> float:
    """
    Оценивает «матч» по ключевым словам.
    Комбинируем Jaccard (|∩| / |∪|) и покрытие JD (|∩| / |JD|).
    Возвращаем проценты 0..100 с одной цифрой после запятой.
    """
    s1 = {str(x).lower().strip() for x in resume_kw if str(x).strip()}
    s2 = {str(x).lower().strip() for x in jd_kw if str(x).strip()}
    if not s1 or not s2:
        return 0.0

    inter = len(s1 & s2)
    union = len(s1 | s2)
    jaccard = inter / union if union else 0.0
    coverage = inter / len(s2) if s2 else 0.0

    score = 0.6 * coverage + 0.4 * jaccard
    return round(score * 100.0, 1)

