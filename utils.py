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
            return "\n".join(t)
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

def check_ats_readability(resume_text: str, file_name: str = "") -> dict:
    """
    Проверяет резюме на совместимость с ATS системами.
    Возвращает словарь с результатами проверки и рекомендациями.
    """
    if not resume_text:
        return {
            "score": 0,
            "status": "critical",
            "issues": ["No text could be extracted from the resume"],
            "recommendations": ["Check if the file format is supported", "Try converting to a different format"],
            "ats_friendly": False
        }
    
    # Calculate readability metrics
    total_chars = len(resume_text)
    total_words = len(resume_text.split())
    total_lines = len(resume_text.split('\n'))
    
    # Check for common ATS issues
    issues = []
    recommendations = []
    
    # Issue 1: Text too short (might be image-based PDF)
    if total_words < 50:
        issues.append("Very short text extracted - might be an image-based PDF")
        recommendations.append("Convert to text-based PDF or use Word document")
    
    # Issue 2: Too many special characters (might be OCR artifacts)
    special_char_ratio = len(re.findall(r'[^\w\s]', resume_text)) / max(1, total_chars)
    if special_char_ratio > 0.3:
        issues.append("High number of special characters - might be OCR artifacts")
        recommendations.append("Check if text was properly extracted")
    
    # Issue 3: Check for common ATS-unfriendly patterns (less strict)
    ats_unfriendly_patterns = [
        (r'[^\x00-\x7F]', "Non-ASCII characters detected"),
        (r'\b[A-Z]{5,}\b', "Excessive all-caps text detected (harder for ATS to parse)"),
        # Only flag really unusual characters, not common punctuation
        (r'[^\w\s\-\.\,\;\:\!\?\(\)\[\]\{\}\"\']', "Unusual formatting characters detected"),
    ]
    
    for pattern, issue_desc in ats_unfriendly_patterns:
        if re.search(pattern, resume_text):
            issues.append(issue_desc)
    
    # Issue 4: Check if text looks like it was properly extracted
    # Look for signs of image-based PDF or design tool export
    suspicious_patterns = [
        (r'^[^\w]*$', "Lines with no readable text"),
        (r'[A-Za-z]{25,}', "Very long words (might be design artifacts)"),
        (r'\n{5,}', "Excessive line breaks (design tool formatting)"),
    ]
    
    for pattern, issue_desc in suspicious_patterns:
        if re.search(pattern, resume_text):
            issues.append(issue_desc)
    
    # File format specific warnings
    if file_name and file_name.lower().endswith('.pdf'):
        if total_words < 100:
            issues.append("PDF appears to be image-based or design tool export")
            recommendations.append("Export as 'text-based PDF' from your design tool")
            recommendations.append("Or save as Word document (.docx) for better ATS compatibility")
    
    # Calculate overall ATS compatibility score
    score = 100
    
    # Deduct points for each issue
    if total_words < 100:
        score -= 30
    elif total_words < 200:
        score -= 15
    
    if special_char_ratio > 0.3:
        score -= 20
    elif special_char_ratio > 0.2:
        score -= 10
    
    score -= len(issues) * 10
    score = max(0, score)
    
    # Determine status
    if score >= 80:
        status = "excellent"
        ats_friendly = True
    elif score >= 60:
        status = "good"
        ats_friendly = True
    elif score >= 40:
        status = "fair"
        ats_friendly = False
    else:
        status = "poor"
        ats_friendly = False
    
    # Add general recommendations based on score
    if not ats_friendly:
        recommendations.extend([
            "Use simple, clean formatting",
            "Avoid complex layouts and graphics",
            "Use standard fonts (Arial, Calibri, Times New Roman)",
            "Save as .docx or text-based PDF",
            "Test with online ATS checkers"
        ])
    
    return {
        "score": score,
        "status": status,
        "ats_friendly": ats_friendly,
        "issues": issues,
        "recommendations": recommendations,
        "metrics": {
            "total_chars": total_chars,
            "total_words": total_words,
            "total_lines": total_lines,
            "special_char_ratio": round(special_char_ratio, 3)
        }
    }


# =============================================================================
#                           НОРМАЛИЗАЦИЯ / ТОКЕНЫ
# =============================================================================

def clean_text(s: str) -> str:
    """Грубая очистка: убрать \x00, схлопнуть пробелы и нормализовать переносы."""
    if not s:
        return ""
    s = s.replace("\x00", " ")
    

    
    # Then handle the rest normally
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\r\n?", "\n", s)
    return s.strip()


def detect_pdf_formatting_issues(resume_text: str) -> dict:
    """Detect common PDF formatting issues that break ATS systems."""
    issues = []
    recommendations = []
    severity = "low"
    
    # Check for the Figma/design tool export issue
    problematic_lines = []
    for i, line in enumerate(resume_text.split('\n'), 1):
        # Look for lines with many single letters separated by spaces
        if re.search(r'([a-zA-Z]\s+){3,}[a-zA-Z]', line):
            problematic_lines.append((i, line.strip()))
    
    if problematic_lines:
        severity = "high"
        issues.append(f"**PDF Export Issue Detected:** {len(problematic_lines)} lines have broken text formatting")
        issues.append("This commonly happens when exporting PDFs from design tools like Figma, Canva, or Photoshop")
        
        # Show examples of the problem
        issues.append("**Examples of broken text:**")
        for line_num, line in problematic_lines[:3]:  # Show first 3 examples
            issues.append(f"Line {line_num}: `{line[:50]}{'...' if len(line) > 50 else ''}`")
        
        recommendations.append("**Fix this in your design tool:**")
        recommendations.append("• Export as 'text-based PDF' instead of 'image-based PDF'")
        recommendations.append("• Save as Word document (.docx) for better ATS compatibility")
        recommendations.append("• Use 'Print to PDF' option if available")
        recommendations.append("• Check your design tool's PDF export settings")
        
        recommendations.append("**Why this happens:**")
        recommendations.append("Design tools often create PDFs where text is treated as graphics")
        recommendations.append("This makes the text unreadable by ATS systems and job platforms")
    
    return {
        "has_issues": len(problematic_lines) > 0,
        "severity": severity,
        "issues": issues,
        "recommendations": recommendations,
        "problematic_lines_count": len(problematic_lines)
    }

def tokenize(text: str) -> List[str]:
    """Простая токенизация: только букво-цифровые токены длиной >= 2."""
    if not text:
        return []
    return [t for t in re.findall(r"\b\w+\b", text.lower()) if len(t) >= 2]


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
    "flat","company","companies","corporate","corporation","corporations",
    
    # Additional generic/irrelevant words that don't represent skills
    "has","have","had","having","become","becomes","became","becoming",
    "top","main","challenge","challenges","challenging","transform","transforms",
    "transformed","transforming","level","levels","setting","set","sets",
    "standards","standard","hands","hand","find","finds","finding","found",
    "elegant","elegance","attention","detail","details","overall","direction",
    "directions","during","other","others","another","each","every","all",
    "some","many","few","several","various","different","similar","same",
    "first","second","third","next","previous","current","recent","new",
    "old","young","big","small","large","tiny","huge","enormous",
    "important","significant","essential","critical","crucial","vital",
    "major","minor","primary","secondary","tertiary","main","sub",
    "core","central","peripheral","additional","extra","supplementary",
    "complementary","supporting","assisting","helping","aiding","facilitating",
    "enabling","empowering","strengthening","enhancing","improving","bettering",
    "advancing","progressing","developing","evolving","growing","expanding",
    "extending","broadening","widening","deepening","intensifying","strengthening",
    "reinforcing","consolidating","unifying","integrating","connecting","linking",
    "joining","combining","merging","blending","mixing","combining","uniting",
    "bringing","taking","making","doing","performing","executing","carrying",
    "conducting","leading","guiding","directing","managing","overseeing",
    "supervising","coordinating","organizing","arranging","structuring",
    "planning","strategizing","thinking","considering","evaluating","assessing",
    "analyzing","examining","investigating","exploring","researching","studying",
    "learning","understanding","comprehending","grasping","realizing","recognizing",
    "identifying","discovering","finding","locating","spotting","noticing",
    "seeing","observing","watching","monitoring","tracking","following",
    "pursuing","chasing","seeking","searching","looking","finding","discovering"
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
    
    # Additional company-related terms to filter out
    company_related = {"restream", "restreaming", "multistream", "multistreaming"}
    cand -= company_related
    
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
    
    # Role-specific keyword prioritization - focus on actual skills and tools
    role_priority = {
        "product_design": [
            # Core design skills
            "design", "ux", "ui", "prototype", "wireframe", "mockup", "sketch", "figma",
            "user experience", "user interface", "visual", "interaction", "typography",
            "layout", "composition", "color", "branding", "illustration", "iconography",
            
            # Design processes and methods
            "user research", "usability testing", "a/b testing", "design thinking",
            "ideation", "iteration", "feedback", "critique", "design review",
            
            # Design systems and tools
            "design system", "component library", "style guide", "pattern library",
            "sketch", "figma", "adobe", "photoshop", "illustrator", "invision",
            "principle", "framer", "protopie", "marvel", "balsamiq"
        ],
        "engineering": [
            # Programming languages
            "python", "javascript", "java", "c++", "c#", "go", "rust", "swift",
            "kotlin", "typescript", "php", "ruby", "scala", "elixir",
            
            # Technologies and frameworks
            "react", "angular", "vue", "node", "django", "flask", "spring",
            "docker", "kubernetes", "aws", "azure", "gcp", "sql", "nosql",
            
            # Engineering practices
            "agile", "scrum", "tdd", "bdd", "ci/cd", "devops", "microservices"
        ],
        "product_management": [
            # Product strategy
            "strategy", "roadmap", "vision", "mission", "goals", "objectives",
            "requirements", "user stories", "acceptance criteria", "success metrics",
            
            # Market and business
            "market research", "competitive analysis", "business case", "roi",
            "stakeholder management", "cross-functional collaboration"
        ],
        "marketing": [
            # Marketing channels
            "digital marketing", "social media", "email marketing", "content marketing",
            "seo", "sem", "ppc", "affiliate marketing", "influencer marketing",
            
            # Analytics and measurement
            "google analytics", "mixpanel", "amplitude", "conversion optimization",
            "a/b testing", "roi", "cac", "ltv", "engagement", "retention"
        ]
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
    
    # More flexible matching - check if keywords appear in resume text (case-insensitive)
    resume_text_lower = resume_text.lower()
    
    present = []
    missing = []
    
    # Debug: Let's see what we're actually working with
    print(f"DEBUG: JD keys to search for: {jd_keys}")
    print(f"DEBUG: Resume text length: {len(resume_text)}")
    print(f"DEBUG: Resume text sample (first 500 chars): {resume_text[:500]}")
    
    for keyword in jd_keys:
        # Check if keyword appears in resume text (more flexible than exact token match)
        keyword_lower = keyword.lower()
        if keyword_lower in resume_text_lower:
            present.append(keyword)
            print(f"DEBUG: FOUND '{keyword}' in resume")
        else:
            missing.append(keyword)
            print(f"DEBUG: MISSING '{keyword}' - not found in resume")
    
    print(f"DEBUG: Final results - Present: {present}, Missing: {missing}")

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
    
    # Comprehensive section patterns with variations
    section_patterns = {
        'experience': [
            r'\b(?:experience|work\s+experience|employment|work\s+history|professional\s+experience|'
            r'career|work|employment\s+history|professional\s+background|work\s+background)\b'
        ],
        'skills': [
            r'\b(?:skills|technical\s+skills|competencies|expertise|capabilities|proficiencies|'
            r'technologies|tools|software|programming\s+languages|frameworks|libraries)\b'
        ],
        'education': [
            r'\b(?:education|academic|qualifications|degree|university|college|school|'
            r'certification|certifications|training|courses|learning|academic\s+background)\b'
        ],
        'projects': [
            r'\b(?:projects|portfolio|achievements|accomplishments|key\s+projects|'
            r'notable\s+projects|featured\s+work|case\s+studies|work\s+samples)\b'
        ],
        'summary': [
            r'\b(?:summary|profile|objective|about|overview|introduction|'
            r'professional\s+summary|career\s+objective|personal\s+statement)\b'
        ],
        'contact': [
            r'\b(?:contact|personal|links|portfolio|github|linkedin|email|phone|'
            r'address|location|social\s+media|online\s+presence|websites)\b'
        ],
        'languages': [
            r'\b(?:languages|certifications|courses|training|certificates|'
            r'licenses|accreditations|professional\s+development|continuing\s+education)\b'
        ],
        'interests': [
            r'\b(?:volunteer|interests|hobbies|activities|volunteer\s+work|'
            r'community\s+service|extracurricular|personal\s+interests|additional\s+activities)\b'
        ]
    }
    
    text_lower = resume_text.lower()
    lines = text_lower.split('\n')
    
    found_sections = set()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # More flexible header detection - look for various formats
        # 1. Lines that start with capital letters
        # 2. Lines in ALL CAPS
        # 3. Lines with common section indicators
        # 4. Lines containing section keywords anywhere
        is_header = False
        
        # Check if line starts with capital letter
        if line and line[0].isupper():
            is_header = True
        # Check if line is in ALL CAPS (common in resumes)
        elif line.isupper() and len(line) > 2:
            is_header = True
        # Check if line has common section indicators
        elif any(indicator in line for indicator in ['experience', 'skills', 'education', 'projects', 'summary', 'contact']):
            is_header = True
        # Check if line contains section keywords anywhere (more flexible)
        elif any(keyword in line for keyword in ['experience', 'skills', 'education', 'projects', 'summary', 'contact', 'work', 'employment', 'career', 'background', 'portfolio', 'achievements']):
            is_header = True
        
        if is_header:
            # Check each section type
            for section_name, patterns in section_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line):
                        found_sections.add(section_name)
                        break
                if section_name in found_sections:
                    break
    
    # Also check for sections that might be mentioned in the text content
    # This helps catch sections that might not have clear headers
    for section_name, patterns in section_patterns.items():
        if section_name not in found_sections:
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    found_sections.add(section_name)
                    break
    
    return found_sections
