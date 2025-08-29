# utils.py
# -*- coding: utf-8 -*-

import re
from collections import Counter
from typing import List, Set, Tuple, Iterable

# =============================================================================
#               ЧТЕНИЕ ТЕКСТА ИЗ ФАЙЛОВ (PDF / DOCX / TXT)
# =============================================================================

def extract_text_from_file(file) -> str:
    """
    Принимает st.file_uploader объект и вытягивает текст из PDF/DOCX/TXT.
    Возвращает строку (может быть пустой, если парсинг не удался).
    """
    if not file:
        return ""

    name = (getattr(file, "name", "") or "").lower()

    # --- TXT ---
    if name.endswith(".txt"):
        data = file.read()
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            try:
                return data.decode("latin-1", errors="ignore")
            except Exception:
                return ""

    # --- PDF ---
    if name.endswith(".pdf"):
        try:
            from PyPDF2 import PdfReader
        except Exception:
            return ""
        try:
            reader = PdfReader(file)
            parts: List[str] = []
            for p in reader.pages:
                t = p.extract_text() or ""
                if t:
                    parts.append(t)
            return "\n".join(parts)
        except Exception:
            return ""

    # --- DOCX ---
    if name.endswith(".docx"):
        try:
            import docx  # python-docx
        except Exception:
            return ""
        try:
            doc = docx.Document(file)
            return "\n".join(p.text for p in doc.paragraphs if p.text)
        except Exception:
            return ""

    # --- Fallback: пробуем прочитать как текст ---
    try:
        data = file.read()
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""


# =============================================================================
#                           НОРМАЛИЗАЦИЯ / ТОКЕНЫ
# =============================================================================

def clean_text(s: str) -> str:
    """Грубая очистка: убрать \x00, схлопнуть пробелы и нормализовать переносы."""
    if not s:
        return ""
    s = s.replace("\x00", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\r\n?", "\n", s)
    return s.strip()

def tokenize(text: str) -> List[str]:
    """Простая токенизация: только букво-цифровые токены длиной >= 3."""
    if not text:
        return []
    return [t for t in re.findall(r"\b\w+\b", text.lower()) if len(t) > 2]


# =============================================================================
#                СТОП-ЛИСТЫ: компания/география/филлера/«пух»
# =============================================================================

COMPANY_SUFFIXES = r"(?:inc|llc|gmbh|ltd|plc|corp|co|sa|ag|oy|kk|pte|pty|s\.?r\.?l\.?|s\.?a\.?s\.?|asa|ab|bv|nv)\b"

# Общее «служебное» — предлоги/союзы/частицы и т.п.
FILLER_STOP: Set[str] = set("""
including include includes about across within among between various multiple
customer customers client clients team teams company companies business businesses
join hiring hire role roles position opportunity opportunities responsibilities requirements
will would may can could must should via using use uses used
and or the a an for with of to in on at by from as is are was were be been being
your you we they our their this that these those it its into acrosses
""".split())

# «пушистые»/общие/водяные слова (добавлены те, что мешали в тестах)
FLUFF_STOP: Set[str] = {
    # Общие пустые
    "real","meaningful","believe","working","make","take","one","what","join","explore",
    "solutions","solution","opportunity","impact","value","role","responsibility",
    "responsibilities","requirements","offer","offers","needed","desired","preferred",
    "skills","skill","experience","experiences","knowledge","understanding","background",
    "ability","capable","strong","excellent","good","great","big",

    # «Вода»-глаголы
    "help","work","drive","support","develop","improve","ensure","deliver",
    "collaborate","collaboration","provide","including","build","building","contribute",

    # Функциональные общие
    "team","teams","environment","organization","organizational","project","projects",
    "business","customers","client","clients","stakeholders","company","companies",

    # Прилагательные без смысла
    "fast","innovative","new","next","future","current","global","local",
    "international","stronger","better","best","leading","unique","key","important",

    # «Везде и ни о чем»
    "platform","system","systems","process","processes","approach","methods","tools",
    "culture","focus","needs","goal","vision","mission","strategy","strategic",

    # Немного частых слов
    "more","high","low","many","across","around","different","various",

    # Конкретные, мешавшие в примерах
    "service","services","sales","offerings"
}

# География/локали
GEO_STOP: Set[str] = set("""
nordic nordics europe european cet cest oslo helsinki stockholm norway sweden finland
germany france uk britain england denmark iceland scandinavia
""".split())

def _norm_company_name(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^\w\s.-]", " ", s)
    s = re.sub(rf"\b{COMPANY_SUFFIXES}\.?$", "", s.strip())
    return re.sub(r"[\s._-]+", " ", s).strip()

def detect_company_names(jd_text: str) -> Set[str]:
    """
    Пытаемся вытащить название компании из JD без внешних NLP-либ:
    - первые 3 строки заголовка
    - паттерны 'at X', 'About X', 'Join X', 'We at X'
    - паттерн 'X is|are hiring|looking'
    - домены в ссылках и email
    Возвращаем нормализованные имена.
    """
    cand: Set[str] = set()
    text = jd_text or ""
    lower = text.lower()

    # 1) первые три строки — там часто бренд
    head = "\n".join(text.splitlines()[:3])
    caps = re.findall(
        r"\b([A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){0,2})(?:\s+" + COMPANY_SUFFIXES + r")?\b",
        head
    )
    for s in caps:
        cand.add(_norm_company_name(s))

    # 2) 'at X' / 'About X' / 'Join X' / 'We at X'
    for m in re.findall(r"\b(?:at|about|join|we at)\s+([A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){0,2})", text):
        cand.add(_norm_company_name(m))

    # 3) 'X is|are hiring|looking'
    for m in re.findall(r"\b([A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){0,2})\s+(?:is|are)\s+(?:hiring|looking)", text):
        cand.add(_norm_company_name(m))

    # 4) домены
    for dom in re.findall(r"https?://(?:www\.)?([a-z0-9-]+)\.(?:com|io|ai|co|tech|net|org|no|se|fi|uk|de|fr)\b", lower):
        cand.add(_norm_company_name(dom))
    for dom in re.findall(r"\b[a-z0-9._%+-]+@([a-z0-9-]+)\.(?:com|io|ai|co|tech|net|org|no|se|fi|uk|de|fr)\b", lower):
        cand.add(_norm_company_name(dom))

    # явный мусор
    cand -= {"careers", "jobs", "hiring", "company"}
    return {c for c in cand if c}


# =============================================================================
#                                КЛЮЧЕВЫЕ СЛОВА
# =============================================================================

def top_keywords(jd_text: str, top_n: int = 30) -> List[str]:
    """
    Извлекает ключевые слова из JD, отфильтровав:
      • название компании (и его части),
      • географию,
      • «филлера»/«пушистые» слова.
    Возвращает список максимум из top_n токенов.
    """
    tokens = tokenize(jd_text)
    companies = detect_company_names(jd_text)

    # части названия компании тоже в стоп
    company_parts: Set[str] = set()
    for c in companies:
        company_parts.add(c)
        company_parts.update(c.split())

    stop = FILLER_STOP | FLUFF_STOP | GEO_STOP | company_parts

    freq = Counter(tokens)
    result: List[str] = []
    # небольшое «оверфетч» (берем больше кандидатов, затем фильтруем)
    for w, _cnt in freq.most_common(top_n * 5):
        if not w or w.isdigit():
            continue
        if w in stop:
            continue
        result.append(w)
        if len(result) >= top_n:
            break

    # финальная страховка от попадания «компании» в результат
    result = [w for w in result if w not in companies and w not in company_parts]
    return result


# =============================================================================
#                                МЕТРИКИ/СОВПАДЕНИЯ
# =============================================================================

def compute_keyword_overlap(resume_tokens: List[str], jd_keywords: List[str]) -> Tuple[int, int, float]:
    """
    Простой показатель: |∩|, |JD|, процент покрытия JD.
    """
    rset = set(resume_tokens)
    jset = set(jd_keywords)
    inter = len(rset & jset)
    total = max(1, len(jset))
    score = round(100.0 * inter / total, 1)
    return inter, total, score

def compute_similarity(resume_kw: Iterable[str], jd_kw: Iterable[str]) -> float:
    """
    Комбинированная метрика схожести (0..100):
    0.6 * покрытие JD  +  0.4 * Jaccard.
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


# =============================================================================
#                       ПОДСКАЗКИ ПО ОТСУТСТВУЮЩИМ КЛЮЧАМ
# =============================================================================

def suggest_missing_keywords(
    jd_text: str,
    resume_text: str,
    top_n: int = 30,
    visibility_threshold: int = 1,
) -> Tuple[List[str], List[str], float]:
    """
    Возвращает кортеж (present, missing, coverage):
      • present — ключевые слова из JD, которые «видимы» в резюме (встречаются >= threshold),
      • missing — ключевые слова из JD, которых мало/нет в резюме,
      • coverage — интегральная оценка совпадения (0..100).
    """
    jd_keys: List[str] = top_keywords(jd_text, top_n=top_n)

    res_tokens = tokenize(resume_text)
    res_freq = Counter(res_tokens)

    present = [w for w in jd_keys if res_freq.get(w, 0) >= visibility_threshold]
    missing = [w for w in jd_keys if res_freq.get(w, 0) < visibility_threshold]

    coverage = compute_similarity(resume_kw=res_tokens, jd_kw=jd_keys)
    return present, missing, coverage
