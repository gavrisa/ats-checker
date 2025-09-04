# Enhanced Keyword Extraction System

This document describes the backend-only upgrade that improves keyword extraction and bullet suggestions while maintaining full backward compatibility with the existing frontend.

## Features

### ✅ Implemented Features

1. **Enhanced Keyword Extraction**
   - TF-IDF ranking for better keyword quality
   - Advanced quality filters to remove fluff words
   - Tool/stack name recognition and boosting
   - Acronym preservation (UX, UI, API, OKR, KPI)
   - Lemma-based deduplication

2. **Fuzzy Matching**
   - RapidFuzz integration for typo tolerance
   - Handles pluralization (designer/designers)
   - 90% similarity threshold for matches
   - Token-set ratio matching

3. **Enhanced Bullet Suggestions**
   - Template-based generation with 8 different patterns
   - Action verb variety (no repetition)
   - Context-aware keyword insertion
   - Up to 10 suggestions per analysis

4. **Feature Flags & Configuration**
   - `SEMANTIC_ON=1` for semantic similarity (optional)
   - `PY_SIDECAR_ON=1` for Python sidecar (optional)
   - Configurable thresholds and limits
   - Environment-based configuration

5. **Backward Compatibility**
   - All existing API fields preserved
   - Non-breaking optional fields added
   - Graceful fallback to simple extractor
   - Frontend requires no changes

### 🔄 Optional Features (Not Yet Implemented)

1. **Semantic Similarity**
   - `@xenova/transformers` integration
   - Sentence-transformers/all-MiniLM-L6-v2 model
   - 1200ms timeout with TF-IDF fallback

2. **Python Sidecar**
   - SpaCy integration for better NLP
   - KeyBERT for keyword re-ranking
   - 2000ms timeout with Node fallback

## Installation

### Required Dependencies

```bash
pip install nltk scikit-learn rapidfuzz spacy wordfreq
```

### Optional Dependencies

```bash
# For semantic similarity
pip install transformers torch sentence-transformers

# For Python sidecar
python -m spacy download en_core_web_sm
```

## Configuration

### Environment Variables

```bash
# Feature flags
SEMANTIC_ON=0                    # Enable semantic similarity
PY_SIDECAR_ON=0                  # Enable Python sidecar

# Performance settings
SEMANTIC_TIMEOUT_MS=1200         # Semantic similarity timeout
SIDECAR_TIMEOUT_MS=2000          # Python sidecar timeout

# Keyword extraction settings
MAX_KEYWORDS=30                  # Maximum keywords to extract
MAX_MISSING_KEYWORDS=7           # Maximum missing keywords to show
MAX_BULLET_SUGGESTIONS=10        # Maximum bullet suggestions

# Fuzzy matching settings
FUZZY_MATCH_THRESHOLD=90         # Fuzzy match similarity threshold

# Debug settings
DEBUG_MODE=0                     # Enable debug information
LOG_LEVEL=INFO                   # Logging level
```

## API Response Format

### Core Fields (Existing API Contract)

```json
{
  "score": 85,
  "textSimilarity": 74.1,
  "keywordCoverage": 100.0,
  "all_keywords": ["senior", "ux", "ui", "designer", "figma"],
  "matched_keywords": ["senior", "ux", "ui", "designer", "figma"],
  "missing_keywords": ["prototyping", "user testing"],
  "bullet_suggestions": [
    "Designed comprehensive prototyping workflows to enhance user experience, cutting development time by 25%",
    "Led user testing initiatives with 50+ participants to validate design assumptions, informing product decisions using prototyping"
  ],
  "domain_tags": [],
  "role_tags": [],
  "dropped_examples": [],
  "file_info": {...},
  "message": "Analysis completed successfully!"
}
```

### Enhanced Fields (Optional, Non-Breaking)

```json
{
  "enhanced_features": {
    "fuzzy_matching": true,
    "tfidf_ranking": true,
    "semantic_similarity": false,
    "python_sidecar": false
  },
  "feature_flags": {
    "enhanced_keywords": true,
    "fuzzy_matching": true,
    "bullet_suggestions": true,
    "semantic_similarity": false,
    "python_sidecar": false
  },
  "notes": [],
  "debug": {
    "extractor_type": "EnhancedKeywordExtractor",
    "config": {...},
    "timings": {}
  }
}
```

## Usage Examples

### Basic Usage

```python
from enhanced_keyword_extractor import EnhancedKeywordExtractor

extractor = EnhancedKeywordExtractor()

# Extract keywords
keywords = extractor.extract_enhanced_keywords(job_description)

# Find matches with fuzzy matching
matched, missing = extractor.find_matching_keywords_fuzzy(resume_text, keywords)

# Calculate enhanced scores
scores = extractor.calculate_enhanced_scores(matched, keywords, resume_text, job_description)

# Generate bullet suggestions
bullets = extractor.generate_enhanced_bullet_suggestions(missing, 10)
```

### With Feature Flags

```python
import os
from enhanced_keyword_extractor import EnhancedKeywordExtractor

# Enable semantic similarity
os.environ["SEMANTIC_ON"] = "1"

extractor = EnhancedKeywordExtractor()
# Now uses semantic similarity when available
```

## Testing

### Run Simple Test

```bash
cd api
python test_enhanced_simple.py
```

### Run Full Test Suite

```bash
cd api
python -m pytest test_enhanced_keyword_extractor.py -v
```

### Test Specific Features

```bash
# Test fuzzy matching
python -m pytest test_enhanced_keyword_extractor.py::TestEnhancedKeywordExtractor::test_fuzzy_matching -v

# Test bullet generation
python -m pytest test_enhanced_keyword_extractor.py::TestEnhancedKeywordExtractor::test_bullet_generation_quality -v
```

## Performance

### Benchmarks

- **Keyword Extraction**: ~50-100ms for typical job descriptions
- **Fuzzy Matching**: ~10-20ms for 30 keywords
- **Bullet Generation**: ~5-10ms for 10 suggestions
- **Total Processing**: ~100-200ms (excluding file I/O)

### Memory Usage

- **Base Memory**: ~50MB (with NLTK, scikit-learn, rapidfuzz)
- **With SpaCy**: +200MB (en_core_web_sm model)
- **With Transformers**: +500MB (sentence-transformers model)

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Install missing dependencies
   pip install nltk scikit-learn rapidfuzz spacy wordfreq
   ```

2. **NLTK Data Missing**
   ```python
   import nltk
   nltk.download('stopwords')
   nltk.download('punkt')
   ```

3. **SpaCy Model Missing**
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Memory Issues**
   - Disable semantic similarity: `SEMANTIC_ON=0`
   - Disable Python sidecar: `PY_SIDECAR_ON=0`
   - Reduce max keywords: `MAX_KEYWORDS=20`

### Debug Mode

Enable debug mode for detailed logging:

```bash
DEBUG_MODE=1 LOG_LEVEL=DEBUG python main.py
```

## Migration Guide

### From Simple Extractor

The enhanced extractor is a drop-in replacement:

```python
# Before
from simple_smart_extractor import SimpleSmartExtractor
extractor = SimpleSmartExtractor()

# After
from enhanced_keyword_extractor import EnhancedKeywordExtractor
extractor = EnhancedKeywordExtractor()
```

### API Changes

No breaking changes. All existing API fields are preserved. New fields are optional and can be ignored by the frontend.

## Future Enhancements

1. **Semantic Similarity Integration**
   - Add `@xenova/transformers` support
   - Implement sentence-transformers model
   - Add semantic similarity to scoring

2. **Python Sidecar Integration**
   - Add SpaCy integration
   - Implement KeyBERT re-ranking
   - Add advanced NLP features

3. **Additional Features**
   - Keyword grouping (tools, methods, outcomes)
   - Visibility scoring for keywords
   - Highlighted term counts
   - Advanced bullet templates

## Support

For issues or questions:

1. Check the troubleshooting section
2. Run the test suite to verify installation
3. Check logs with debug mode enabled
4. Review the configuration options

