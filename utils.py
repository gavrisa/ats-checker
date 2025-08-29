import re
from collections import Counter
from typing import List, Set

# --- простые эвристики для выделения компаний/географии/филлеров ---

COMPANY_SUFFIXES = r"(?:inc|llc|gmbh|ltd|plc|corp|co|sa|ag|oy|kk|pte|pty|s\.?r\.?l\.?|s\.?a\.?s\.?|asa|ab|bv|nv)\b"

FILLER_STOP: Set[str] = set("""
including include includes about across within among between various multiple
customer customers client clients team teams company companies business businesses
join hiring hire role roles position opportunity opportunities responsibilities requirements
will would may can could must should via using use uses used
and or the a an for with of to in on at by from as is are was were be been being
your you we they our their this that these those it its into acrosses
""".split())

# «Пушистый» стоп-лист: корпоративная вода, общие слова, лишние прилагательные
FLUFF_STOP: Set[str] = {
    # общие пустые слова
    "real", "meaningful", "believe", "working", "make", "take", "one", "what", "join", "explore",
    "solutions", "solution", "opportunity", "impact", "value", "role", "responsibility",
    "responsibilities", "requirements", "offer", "offers", "needed", "desired", "preferred",
    "skills", "skill", "experience", "experiences", "knowledge", "understanding", "background",
    "ability", "capable", "strong", "excellent", "good", "great", "big",

    # водяные глаголы
    "help", "work", "drive", "support", "develop", "improve", "ensure", "deliver",
    "collaborate", "collaboration", "provide", "including", "build", "building", "contribute",

    # функциональные общие
    "team", "teams", "environment", "organization", "organizational", "project", "projects",
    "business", "customers", "client", "clients", "stakeholders", "company", "companies",
    "service", "services", "sales", "offerings",

    # прилагательные без смысла
    "fast", "innovative", "new", "next", "future", "current", "global", "local",
    "international", "stronger", "better", "best", "leading", "unique", "key", "important",

    # частые «везде и ни о чём»
    "platform", "system", "systems", "process", "processes", "approach", "methods", "tools",
    "culture", "focus", "needs", "goal", "vision", "mission", "strategy", "strategic",

    # мелочь
    "more", "high", "low", "many", "across", "around", "different", "various"
}

GEO_STOP: Set[str] = set("""
nordic nordics europe european cet cest oslo helsinki stockholm norway sweden finland
germany france uk britain england denmark iceland scandinavia
""".split())


# --- нормализация и детекция компании ---

def _norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^\w\s.-]", " ", s)        # убрать пунктуацию кроме .- (для Inc., Co.)
    s = re.sub(rf"\b{COMPANY_SUFFIXES}\.?$", "", s.strip())  # убрать суффиксы юр.форм
    s = re.sub(r"['’]s$", "", s)            # possessive: company's -> company
    s = re.sub(r"s$", "", s)                # простая лемматизация мн.числа: services -> service
    return re.sub(r"[\s._-]+", " ", s).strip()

def detect_company_names(jd_text: str) -> Set[str]:
    """
    Пытаемся найти название компании без внешних зависимостей:
    - заголовок/первые строки
    - фразы вида 'at X', 'About X', 'We at X', 'X is hiring'
    - домены в ссылках/почте
    """
    cand: Set[str] = set()
    text = jd_text.strip()
    lower = text.lower()

    # 1) первые 3 строки — часто там бренд
    first = "\n".join(text.splitlines()[:3])
    caps = re.findall(
        r"\b([A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){0,2})(?:\s+" + COMPANY_SUFFIXES + r")?\b",
        first
    )
    for s in caps:
        cand.add(_norm(s))

    # 2) шаблоны
    for m in re.findall(r"\b(?:at|about|join|we at)\s+([A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){0,2})", text):
        cand.add(_norm(m))

    for m in re.findall(r"\b([A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){0,2})\s+(?:is|are)\s+(?:hiring|looking)", text):
        cand.add(_norm(m))

    # 3) домены
    for dom in re.findall(r"https?://(?:www\.)?([a-z0-9-]+)\.(?:com|io|ai|co|tech|net|org|no|se|fi|uk|de|fr)\b", lower):
        cand.add(_norm(dom))
    for dom in re.findall(r"\b[a-z0-9._%+-]+@([a-z0-9-]+)\.(?:com|io|ai|co|tech|net|org|no|se|fi|uk|de|fr)\b", lower):
        cand.add(_norm(dom))

    cand -= {"careers", "jobs", "hiring", "company"}
    return {c for c in cand if c}


# --- токенизация ---

def tokenize(text: str) -> List[str]:
    # простая «словная» токенизация, без коротких токенов
    return [t for t in re.findall(r"\b\w+\b", text.lower()) if len(t) > 2]


# --- выбор ключевых слов ---

def top_keywords(jd_text: str, top_n: int = 30) -> List[str]:
    """
    Возвращает топ ключевых слов из JD:
    - динамически выкидывает название компании (и его части),
    - выкидывает географию, филлеры и «пушистые» слова,
    - подчищает результат повторно (на случай, если что-то просочилось).
    """
    tokens = tokenize(jd_text)

    # динамический стоп-лист: найденные названия + их части
    companies = detect_company_names(jd_text)
    company_parts: Set[str] = set()
    for c in companies:
        company_parts.add(c)
        company_parts.update(c.split())

    # общий стоп-лист
    stop = FILLER_STOP | FLUFF_STOP | GEO_STOP | company_parts

    # частотная выборка
    freq = Counter(tokens)
    result: List[str] = []
    for w, _cnt in freq.most_common(top_n * 5):  # небольшой оверфетч
        if not w or w.isdigit():
            continue
        if w in stop:
            continue
        # доп-отсев часто-бессодержательных термов
        if w in {"global", "including", "services", "solutions", "across", "value", "impact"}:
            continue
        result.append(w)
        if len(result) >= top_n:
            break

    # финальная очистка от компаний (на всякий случай)
    result = [w for w in result if w not in companies and w not in company_parts]

    return result
