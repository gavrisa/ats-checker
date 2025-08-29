import re
from collections import Counter
from typing import List, Set

# --- эвристики для компаний/географии/филлеров ---

COMPANY_SUFFIXES = r"(?:inc|llc|gmbh|ltd|plc|corp|co|sa|ag|oy|kk|pte|pty|s\.?r\.?l\.?|s\.?a\.?s\.?|asa|ab|bv|nv)\b"

FILLER_STOP: Set[str] = set("""
including include includes about across within among between various multiple
customer customers client clients team teams company companies business businesses
join hiring hire role roles position opportunity opportunities responsibilities requirements
will would may can could must should via using use uses used
and or the a an for with of to in on at by from as is are was were be been being
your you we they our their this that these those it its into acrosses
""".split())

GEO_STOP: Set[str] = set("""
nordic nordics europe european cet cest oslo helsinki stockholm norway sweden finland
germany france uk britain england denmark iceland scandinavia
""".split())

def _norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^\w\s.-]", " ", s)
    s = re.sub(rf"\b{COMPANY_SUFFIXES}\.?$", "", s.strip())
    return re.sub(r"[\s._-]+", " ", s).strip()

def detect_company_names(jd_text: str) -> Set[str]:
    """Пытаемся найти название компании по нескольким шаблонам (без внешних либ)."""
    cand: Set[str] = set()
    text = jd_text.strip()
    lower = text.lower()

    # 1) первые 3 строки — часто там бренд/заголовок
    first = "\n".join(text.splitlines()[:3])
    caps = re.findall(
        r"\b([A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){0,2})(?:\s+" + COMPANY_SUFFIXES + r")?\b",
        first
    )
    for s in caps:
        cand.add(_norm(s))

    # 2) шаблоны 'at X', 'About X', 'Join X', 'We at X'
    for m in re.findall(r"\b(?:at|about|join|we at)\s+([A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){0,2})", text):
        cand.add(_norm(m))

    # 3) 'X is hiring/looking…'
    for m in re.findall(r"\b([A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){0,2})\s+(?:is|are)\s+(?:hiring|looking)", text):
        cand.add(_norm(m))

    # 4) домены ссылок/почты → имя до зоны
    for dom in re.findall(r"https?://(?:www\.)?([a-z0-9-]+)\.(?:com|io|ai|co|tech|net|org|no|se|fi|uk|de|fr)\b", lower):
        cand.add(_norm(dom))
    for dom in re.findall(r"\b[a-z0-9._%+-]+@([a-z0-9-]+)\.(?:com|io|ai|co|tech|net|org|no|se|fi|uk|de|fr)\b", lower):
        cand.add(_norm(dom))

    # убрать явный мусор
    cand -= {"careers", "jobs", "hiring", "company"}
    return {c for c in cand if c}

def tokenize(text: str) -> List[str]:
    return [t for t in re.findall(r"\b\w+\b", text.lower()) if len(t) > 2]

def top_keywords(jd_text: str, top_n: int = 30) -> List[str]:
    """
    Формирует список ключевых слов из JD, автоматически игнорируя название компании,
    географию и общие филлеры. Сигнатура сохранена (принимаем исходный JD).
    """
    tokens = tokenize(jd_text)

    # dynamic stop: найденные названия компании + их части
    companies = detect_company_names(jd_text)
    company_parts: Set[str] = set()
    for c in companies:
        company_parts.add(c)
        company_parts.update(c.split())

    stop = FILLER_STOP | GEO_STOP | company_parts

    # частотная выборка с фильтрами
    freq = Counter(tokens)
    result: List[str] = []
    for w, _cnt in freq.most_common(top_n * 5):
        if w.isdigit():
            continue
        if w in stop:
            continue
        # отбрасываем год/месяцы и слишком «общие» бизнес-слова
        if w in {"global","including","services","solutions","across","value","impact"}:
            continue
        result.append(w)
        if len(result) >= top_n:
            break
    return result
