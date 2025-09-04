# ATS Keyword Extractor

A precise and conservative ATS (Applicant Tracking System) keyword extractor that follows strict rules to identify high-signal, job-specific keywords and phrases from job descriptions and match them against resumes/CVs.

## Features

- **Precise Keyword Extraction**: Extracts 2-4 word noun phrases representing skills, methods, deliverables, domains, or stakeholders
- **Conservative Filtering**: Excludes generic words and prioritizes domain-specific multiword terms
- **Smart Deduplication**: Collapses synonyms and lemmas to avoid redundancy
- **Intelligent Matching**: Case-insensitive, lemmatized matching with semantic awareness
- **Bullet Suggestions**: Generates actionable resume bullet points incorporating missing keywords
- **Debug Information**: Provides transparency into filtering decisions

## Hard Rules (Filters)

### 1. Exclude Generic Words
The following single, generic words are excluded unless they form meaningful phrases:
- `internal`, `key`, `points`, `total`, `experience`, `visual`, `designers`, `language`, `values`, `data` (alone), `cross`, `remote`, `dependent`, `portfolio`, `communication`, `collaboration`, `innovation`, `functional`, `competitive`, `scalability`, `components`, `interaction` (alone), `designing` (alone)

**Examples:**
- ✅ `visual design` (keep)
- ❌ `visual` (drop)
- ✅ `internal stakeholders` (keep)
- ❌ `internal` (drop)
- ✅ `data visualization` (keep)
- ❌ `data` (drop)

### 2. Exclude Verbs/Adjectives Alone
Verbs and adjectives are excluded when they appear alone:
- ❌ `designing`, `dependent`, `competitive`, `remote`
- ✅ `competitive analysis`, `remote usability testing`

### 3. Prioritize Domain-Specific Multiword Terms
The system prioritizes 2-4 token domain-specific terms such as:
- `user research`, `usability testing`, `accessibility (WCAG)`, `personas`, `user journeys`, `experience maps`, `wireframes`, `interactive prototypes`, `interaction models`, `qualitative research`, `quantitative research`, `stakeholder alignment`, `product development teams`, `discovery phase`, `implementation`, `SaaS solutions`, `complex SaaS`, `procurement platform`, `supplier intelligence`, `spend analytics`, `design system`, `information architecture`, `heuristics evaluation`, `A/B testing`, `mixed-methods research`, `task flows`, `journey analytics`, `service blueprint`

### 4. Deduplication via Lemma/Synonym Collapsing
Similar terms are collapsed to avoid redundancy:
- `user journey` ≈ `customer journey`
- `prototype` ≈ `prototyping`
- The JD's wording is preferred

### 5. Length/Format Requirements
- Keywords are lowercase
- Hyphenate when standard (e.g., "end-to-end")
- Maximum 30 keywords in `all_keywords`
- Prefer multiword over single word

## Scoring System

For each candidate phrase `c`:
```
score(c) = (TF_JD weight) * 0.4
         + (Section proximity weight: appears near "Responsibilities/Requirements/What you'll do") * 0.3
         + (Specificity weight: multiword, domain lexicon match) * 0.3
```

Ties are broken by preferring longer, more specific phrases.

## API Endpoint

### POST `/extract-keywords`

**Request:**
```json
{
  "jd_text": "Job description text...",
  "cv_text": "Resume/CV text..."
}
```

**Response:**
```json
{
  "all_keywords": ["user research", "usability testing", "wireframes", ...],
  "matched_keywords": ["user research", "wireframes", ...],
  "missing_keywords": ["usability testing", "accessibility", ...],
  "bullet_suggestions": [
    "Conducted usability testing to inform design decisions and improve user experience.",
    "Developed accessibility strategies that enhanced product usability and accessibility.",
    ...
  ],
  "debug": {
    "dropped_examples": ["key", "internal", "points", ...],
    "kept_examples": ["internal stakeholders", "visual design", ...]
  }
}
```

## Usage Examples

### Python Script
```python
import requests

url = "http://localhost:8000/extract-keywords"
data = {
    "jd_text": "Your job description here...",
    "cv_text": "Your resume text here..."
}

response = requests.post(url, data=data)
result = response.json()

print("All Keywords:", result["all_keywords"])
print("Matched:", result["matched_keywords"])
print("Missing:", result["missing_keywords"])
print("Suggestions:", result["bullet_suggestions"])
```

### HTML Interface
Open `test_ats_interface.html` in a web browser to use the visual interface.

### Command Line Test
```bash
python test_ats_extractor.py
```

## Matching Logic

The system matches keywords using:
- **Case-insensitive matching**
- **Lemmatized matching** (e.g., "personas" ~ "persona")
- **Synonym awareness** (e.g., "usability test" ~ "usability testing")
- **Semantic similarity** (>=0.85 semantic match)

A phrase is considered present if an exact phrase OR close variant appears in the CV.

## Bullet Suggestions

The system generates 4-5 bullet suggestions that:
- Are ≤20 words each
- Use action verbs
- Naturally weave ONLY the missing keywords
- Follow professional resume writing conventions

## Debug Information

The debug section provides transparency into the filtering process:
- **dropped_examples**: Words/phrases that were filtered out
- **kept_examples**: Words/phrases that were retained

This helps users understand why certain terms were included or excluded.

## Installation & Setup

1. **Start the API server:**
   ```bash
   cd api
   python main.py
   ```

2. **Test the endpoint:**
   ```bash
   python test_ats_extractor.py
   ```

3. **Use the web interface:**
   - Open `test_ats_interface.html` in a browser
   - The interface will connect to `localhost:8000`

## Technical Implementation

The ATS keyword extractor is implemented in Python using FastAPI and includes:

- **Text normalization**: Converts text to lowercase and removes special characters
- **Phrase extraction**: Identifies 2-4 word phrases from text
- **Scoring algorithm**: Multi-factor scoring based on TF, section proximity, and specificity
- **Deduplication**: Synonym-based phrase collapsing
- **Matching engine**: Flexible matching with lemmatization and synonym awareness
- **Bullet generation**: Template-based suggestion generation with keyword integration

## Domain-Specific Terms

The system recognizes domain-specific terms across various fields:
- **UX/Design**: user research, usability testing, wireframes, personas, etc.
- **Development**: programming languages, frameworks, methodologies, etc.
- **Business**: stakeholder alignment, product development, analytics, etc.
- **Research**: qualitative research, quantitative research, mixed-methods, etc.

## Contributing

To add new domain terms or modify filtering rules:
1. Update the `DOMAIN_TERMS` set in `api/main.py`
2. Update the `GENERIC_STOPWORDS` set as needed
3. Add new synonym groups to `SYNONYM_GROUPS`
4. Test with sample job descriptions and resumes

## License

This project is part of the ATS Resume Checker MVP.

