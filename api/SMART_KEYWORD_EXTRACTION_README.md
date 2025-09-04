# Smart JD Keyword Extraction & Filtering

This document describes the implementation of the smart keyword extraction system that significantly improves the quality of extracted keywords from job descriptions.

## Overview

The smart keyword extraction system replaces the basic keyword extraction with a comprehensive NLP pipeline that:

1. **Filters out noise and HR filler** (e.g., "built", "meets", "connects", "reviews", "dots", "points rapidly", "ideae")
2. **Keeps meaningful skills/tools/methods/domains** (e.g., "Python", "React", "AWS", "machine learning", "user research")
3. **Handles acronyms intelligently** (e.g., "AI", "ML", "UX", "UI", "API", "QA")
4. **Preserves multi-word phrases** (e.g., "design systems", "stakeholder management", "A/B testing")
5. **Corrects typos** and normalizes variations

## Implementation Status

✅ **Completed:**
- Data files (stopwords, blacklist, tech whitelist, synonyms)
- Normalization pipeline (lowercase, unicode, de-hyphenate)
- Multi-layer noise suppression filters
- YAKE/RAKE ranking with TF-IDF
- Acronym and tech term handling
- Integration with main analysis function
- Fallback to legacy system if dependencies unavailable

## Files Created

### Core Implementation
- `smart_keyword_extractor.py` - Main extraction class
- `data/stopwords_hr.txt` - HR/recruiting stopwords
- `data/blacklist.txt` - Hard-exclude words
- `data/tech_whitelist.txt` - Tech acronyms and tools
- `data/synonyms.json` - Synonym mappings

### Testing & Setup
- `test_smart_keywords.py` - Comprehensive test suite
- `install_smart_dependencies.sh` - Dependency installation script
- `SMART_KEYWORD_EXTRACTION_README.md` - This documentation

## Dependencies

The smart extractor requires these Python packages:

```bash
pip install spacy>=3.7.0
pip install yake>=0.4.8
pip install rake-nltk>=1.0.6
pip install scikit-learn>=1.3.0
pip install wordfreq>=3.0.3
pip install rapidfuzz>=3.0.0
pip install symspellpy>=6.7.7
```

And spaCy English model:
```bash
python -m spacy download en_core_web_sm
```

## How It Works

### 1. Normalization Pipeline
- Lowercase conversion
- Unicode normalization
- Strip punctuation/emoji
- De-hyphenate (end-to-end → end to end)
- Lemmatization with spaCy
- N-gram extraction (2-3 words)

### 2. Noise Suppression
- **Stopwords**: Standard English + HR/recruiting stopwords
- **POS Filter**: Prefer nouns/proper nouns/adjectives
- **NER Filter**: Remove organizations/people/locations
- **Length Filter**: Drop < 3 chars (unless tech acronym)
- **Frequency Filter**: Drop high-frequency generic words
- **Blacklist**: Hard-exclude specific words
- **Typo Correction**: Fix obvious misspellings

### 3. Ranking System
- **YAKE/RAKE**: Base keyword extraction
- **TF-IDF**: Re-rank against full JD
- **Boosts**: +0.15 for multi-word phrases, +0.25 for tech terms
- **Penalties**: -0.2 for generic single words

### 4. Acronym Handling
- Whitelist for common tech acronyms (AI, ML, UX, UI, API, etc.)
- Synonym mapping (UX ↔ user experience, API ↔ application programming interface)
- Normalization of variants

## Usage

The system automatically falls back to the legacy extractor if dependencies are not available:

```python
# In main.py
if smart_extractor:
    logger.info("Using smart keyword extractor")
    jd_keywords_list = smart_extractor.extract_smart_keywords(job_description, 30)
    # ... smart extraction logic
else:
    logger.info("Using legacy keyword extractor")
    # ... legacy extraction logic
```

## Testing

Run the test suite to verify functionality:

```bash
cd api
python3 test_smart_keywords.py
```

The test includes:
- Basic keyword extraction
- Noise filtering verification
- Matching against resume text
- Problematic examples testing

## Expected Improvements

### Before (Legacy System)
```
Keywords: ["built", "meets", "connects", "reviews", "dots", "points", "rapidly", "ideae", "team", "work", "support", "service", "company", "every", "tool", "world", "employer", "status", "reflect", "part", "meeting", "connect", "connected", "review", "reviews", "connect", "connects", "points", "dots", "suitably", "rapidly"]
```

### After (Smart System)
```
Keywords: ["python", "react", "aws", "machine learning", "data analysis", "cloud infrastructure", "web applications", "rest api", "microservices", "postgresql", "redis", "docker", "kubernetes", "git", "jenkins", "jira", "agile", "ci/cd", "version control", "problem solving", "communication skills", "software development", "javascript", "sql", "tensorflow", "pytorch", "ec2", "s3", "lambda", "gcp"]
```

## Performance Considerations

- **Caching**: Results cached by JD hash for incremental updates
- **Debouncing**: 300ms debounce on JD input changes
- **Fallback**: Graceful degradation to legacy system
- **Error Handling**: Comprehensive error handling with logging

## Configuration

The system can be configured by modifying the data files:

- `data/stopwords_hr.txt` - Add/remove HR stopwords
- `data/blacklist.txt` - Add/remove hard-excluded words
- `data/tech_whitelist.txt` - Add/remove tech terms
- `data/synonyms.json` - Add/remove synonym mappings

## Future Enhancements

1. **Domain-specific models**: Train models on specific industries
2. **Real-time learning**: Update filters based on user feedback
3. **Multi-language support**: Extend to other languages
4. **Advanced NER**: Better entity recognition for tools/technologies
5. **Semantic similarity**: Use embeddings for better matching

## Troubleshooting

### Common Issues

1. **Import Errors**: Install dependencies with `install_smart_dependencies.sh`
2. **spaCy Model Missing**: Run `python -m spacy download en_core_web_sm`
3. **Memory Issues**: Reduce max_keywords parameter
4. **Slow Performance**: Check if caching is working properly

### Debug Mode

Enable debug logging to see detailed extraction process:

```python
import logging
logging.getLogger('smart_keyword_extractor').setLevel(logging.DEBUG)
```

## Integration Status

The smart keyword extractor is fully integrated into the main analysis pipeline:

- ✅ Automatic fallback to legacy system
- ✅ Same API interface as legacy system
- ✅ Compatible with existing frontend
- ✅ Comprehensive error handling
- ✅ Performance monitoring and logging

The system will automatically use the smart extractor when dependencies are available, providing significantly better keyword quality while maintaining backward compatibility.


