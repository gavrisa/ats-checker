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
    "service","services","sales","offerings",
    
    # Overused/irrelevant words that don't add value
    "video","videos","people","everyone","anyone","someone","everybody","anybody",
    "lives","life","stories","story","sharing","share","shares","shared",
    "worth","exceptional","unlimited","reach","craft","crafting","content",
    "looking","talented","individual","individuals","who","shares","passion",
    "passionate","believe","believes","believed","mission","dreams","dream",
    "startup","startups","founders","founder","influence","influences","influenced",
    "tech","technology","technologies","get","gets","got","getting","done",
    "back","founded","burning","multistreaming","solution","solutions",
    "inspires","inspired","inspiring","worldwide","world","wide","follow",
    "following","follows","followed","small","highly","driven","focused",
    "lasting","lasting","impact","impacts","impacted","offer","offers","offered",
    "closely","closer","close","build","building","built","grow","growing","grown",
    "evolution","evolve","evolved","evolving","create","creates","created","creating",
    "creator","creators","creation","creative","creativity","influences","influence",
    "influencing","influential","need","needs","needed","job","jobs","work","works",
    "working","worked","environment","environments","structure","structured",
    "flat","company","companies","corporate","corporation","corporations"
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

def detect_role_type(jd_text: str) -> str:
    """
    Определяет тип роли на основе ключевых слов в JD.
    Возвращает строку с типом роли.
    """
    text_lower = jd_text.lower()
    
    # Product Design / UX/UI roles
    design_keywords = {"design", "designer", "ux", "ui", "user experience", "user interface", 
                       "prototype", "wireframe", "mockup", "design system", "visual design"}
    if any(keyword in text_lower for keyword in design_keywords):
        return "product_design"
    
    # Engineering roles
    eng_keywords = {"engineer", "engineering", "developer", "development", "programming", 
                    "code", "software", "technical", "architecture"}
    if any(keyword in text_lower for keyword in eng_keywords):
        return "engineering"
    
    # Product Management roles
    pm_keywords = {"product manager", "product management", "strategy", "roadmap", 
                   "requirements", "stakeholder", "business"}
    if any(keyword in text_lower for keyword in pm_keywords):
        return "product_management"
    
    # Marketing roles
    marketing_keywords = {"marketing", "growth", "acquisition", "campaign", "brand", 
                         "content", "social media", "analytics"}
    if any(keyword in text_lower for keyword in marketing_keywords):
        return "marketing"
    
    return "general"

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
    role_type = detect_role_type(jd_text)

    # части названия компании тоже в стоп
    company_parts: Set[str] = set()
    for c in companies:
        company_parts.add(c)
        company_parts.update(c.split())

    stop = FILLER_STOP | FLUFF_STOP | GEO_STOP | company_parts

    freq = Counter(tokens)
    result: List[str] = []
    
    # Role-specific keyword prioritization
    role_priority = {
        "product_design": ["design", "ux", "ui", "prototype", "wireframe", "mockup", 
                          "user experience", "user interface", "visual", "interaction", 
                          "flow", "system", "quality", "research", "testing"],
        "engineering": ["code", "development", "programming", "architecture", "technical", 
                       "software", "engineering", "system", "performance", "testing"],
        "product_management": ["strategy", "roadmap", "requirements", "stakeholder", 
                              "business", "product", "market", "analysis", "planning"],
        "marketing": ["growth", "acquisition", "campaign", "brand", "content", 
                     "social media", "analytics", "conversion", "engagement"]
    }
    
    # Get priority keywords for the detected role
    priority_keywords = role_priority.get(role_type, [])
    
    # First add priority keywords if they exist
    for keyword in priority_keywords:
        if keyword in freq and keyword not in stop:
            result.append(keyword)
            if len(result) >= top_n:
                break
    
    # Then add remaining high-frequency keywords
    for w, _cnt in freq.most_common(top_n * 5):
        if not w or w.isdigit():
            continue
        if w in stop or w in result:
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

def compute_similarity(resume_text: str, jd_text: str) -> float:
    """
    Вычисляет косинусное сходство между текстами резюме и JD (0..1).
    Использует простой TF-IDF подход без внешних библиотек.
    """
    if not resume_text or not jd_text:
        return 0.0
    
    # Токенизируем тексты
    resume_tokens = tokenize(resume_text)
    jd_tokens = tokenize(jd_text)
    
    if not resume_tokens or not jd_tokens:
        return 0.0
    
    # Создаем словари частот
    resume_freq = Counter(resume_tokens)
    jd_freq = Counter(jd_tokens)
    
    # Получаем все уникальные токены
    all_tokens = set(resume_freq.keys()) | set(jd_freq.keys())
    
    if not all_tokens:
        return 0.0
    
    # Вычисляем TF-IDF векторы (упрощенная версия)
    resume_vector = []
    jd_vector = []
    
    for token in all_tokens:
        # TF (term frequency) - частота токена в документе
        resume_tf = resume_freq.get(token, 0) / max(1, len(resume_tokens))
        jd_tf = jd_freq.get(token, 0) / max(1, len(jd_tokens))
        
        resume_vector.append(resume_tf)
        jd_vector.append(jd_tf)
    
    # Вычисляем косинусное сходство
    dot_product = sum(a * b for a, b in zip(resume_vector, jd_vector))
    
    resume_magnitude = sum(a * a for a in resume_vector) ** 0.5
    jd_magnitude = sum(a * a for a in jd_vector) ** 0.5
    
    if resume_magnitude == 0 or jd_magnitude == 0:
        return 0.0
    
    cosine_similarity = dot_product / (resume_magnitude * jd_magnitude)
    
    # Add safety checks to prevent extreme values
    if cosine_similarity > 1.0:
        # This can happen due to floating point precision issues
        cosine_similarity = 1.0
    elif cosine_similarity < 0.0:
        cosine_similarity = 0.0
    
    return cosine_similarity

def compute_keyword_similarity(resume_kw: Iterable[str], jd_kw: Iterable[str]) -> float:
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

    coverage = compute_keyword_similarity(resume_kw=res_tokens, jd_kw=jd_keys)
    return present, missing, coverage


# =============================================================================
#                           ОБНАРУЖЕНИЕ СЕКЦИЙ РЕЗЮМЕ
# =============================================================================

def detect_sections(resume_text: str) -> Set[str]:
    """
    Обнаруживает стандартные секции резюме на основе заголовков.
    Возвращает множество найденных секций в нижнем регистре.
    """
    if not resume_text:
        return set()
    
    # Паттерны для поиска заголовков секций
    section_patterns = [
        r'\b(?:experience|work\s+experience|employment|work\s+history)\b',
        r'\b(?:skills|technical\s+skills|competencies|expertise)\b',
        r'\b(?:education|academic|qualifications|degree)\b',
        r'\b(?:projects|portfolio|achievements|accomplishments)\b',
        r'\b(?:summary|profile|objective|about)\b',
        r'\b(?:contact|personal|links|portfolio|github|linkedin)\b',
        r'\b(?:languages|certifications|courses|training)\b',
        r'\b(?:volunteer|interests|hobbies|activities)\b'
    ]
    
    # Поиск заголовков (обычно в начале строки, возможно с заглавной буквы)
    text_lower = resume_text.lower()
    lines = text_lower.split('\n')
    
    found_sections = set()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Проверяем, является ли строка заголовком (заглавная буква в начале)
        if line and line[0].isupper():
            for pattern in section_patterns:
                if re.search(pattern, line):
                    # Извлекаем основное слово секции
                    match = re.search(pattern, line)
                    if match:
                        section_name = match.group(0)
                        # Нормализуем название секции
                        if 'experience' in section_name:
                            found_sections.add('experience')
                        elif 'skills' in section_name:
                            found_sections.add('skills')
                        elif 'education' in section_name:
                            found_sections.add('education')
                        elif 'projects' in section_name:
                            found_sections.add('projects')
                        elif 'summary' in section_name or 'profile' in section_name or 'objective' in section_name:
                            found_sections.add('summary')
                        elif 'contact' in section_name or 'personal' in section_name:
                            found_sections.add('contact')
                        elif 'languages' in section_name or 'certifications' in section_name:
                            found_sections.add('languages')
                        elif 'volunteer' in section_name or 'interests' in section_name:
                            found_sections.add('interests')
                        break
    
    return found_sections
