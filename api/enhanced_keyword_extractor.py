"""
Enhanced Keyword Extractor with TF-IDF ranking, fuzzy matching, and bullet suggestions
Implements the backend-only upgrade requirements while maintaining API compatibility.
"""

import re
import json
import logging
import os
import hashlib
from typing import List, Dict, Set, Tuple, Optional, Any
from collections import Counter, defaultdict
from pathlib import Path
import math

# Optional imports with fallbacks
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
    from nltk.tokenize import word_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

logger = logging.getLogger(__name__)

class EnhancedKeywordExtractor:
    """
    Enhanced keyword extractor with TF-IDF ranking, fuzzy matching, and bullet suggestions.
    Maintains backward compatibility with the existing API.
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.cache = {}
        
        # Feature flags from environment
        self.semantic_on = os.getenv("SEMANTIC_ON", "0") == "1"
        self.py_sidecar_on = os.getenv("PY_SIDECAR_ON", "0") == "1"
        
        # Initialize components
        self._load_data_files()
        self._initialize_nlp_components()
        self._initialize_patterns()
        
        # TF-IDF vectorizer
        self.tfidf_vectorizer = None
        if SKLEARN_AVAILABLE:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.8
            )
    
    def _load_data_files(self):
        """Load stopwords, blacklist, tech whitelist, and synonyms."""
        try:
            # Load stopwords
            with open(self.data_dir / "stopwords_hr.txt", "r") as f:
                self.hr_stopwords = set(line.strip().lower() for line in f if line.strip())
            
            # Load blacklist
            with open(self.data_dir / "blacklist.txt", "r") as f:
                self.blacklist = set(line.strip().lower() for line in f if line.strip())
            
            # Load tech whitelist
            with open(self.data_dir / "tech_whitelist.txt", "r") as f:
                self.tech_whitelist = set(line.strip().upper() for line in f if line.strip())
            
            # Load synonyms
            with open(self.data_dir / "synonyms.json", "r") as f:
                self.synonyms = json.load(f)
            
            logger.info("Data files loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading data files: {e}")
            # Fallback to empty sets
            self.hr_stopwords = set()
            self.blacklist = set()
            self.tech_whitelist = set()
            self.synonyms = {}
    
    def _initialize_nlp_components(self):
        """Initialize NLP components with fallbacks."""
        # NLTK components
        if NLTK_AVAILABLE:
            try:
                # Download required NLTK data
                nltk.download('stopwords', quiet=True)
                nltk.download('punkt', quiet=True)
                self.english_stopwords = set(stopwords.words('english'))
                self.stemmer = PorterStemmer()
            except Exception as e:
                logger.warning(f"NLTK initialization failed: {e}")
                self.english_stopwords = self._get_fallback_stopwords()
                self.stemmer = None
        else:
            self.english_stopwords = self._get_fallback_stopwords()
            self.stemmer = None
        
        # SpaCy model (optional)
        self.nlp = None
        if SPACY_AVAILABLE and self.py_sidecar_on:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("SpaCy model loaded successfully")
            except Exception as e:
                logger.warning(f"SpaCy model not available: {e}")
    
    def _get_fallback_stopwords(self) -> Set[str]:
        """Fallback stopwords if NLTK is not available."""
        return {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in', 'is', 'it', 'its',
            'of', 'on', 'that', 'the', 'to', 'was', 'will', 'with', 'you', 'your', 'we', 'our', 'they', 'them',
            'this', 'these', 'those', 'i', 'me', 'my', 'us', 'him', 'her', 'his', 'hers', 'their', 'theirs',
            'am', 'are', 'is', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
            'did', 'doing', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall',
            'if', 'or', 'but', 'so', 'yet', 'nor', 'for', 'and', 'not', 'only', 'also', 'either', 'neither',
            'both', 'all', 'any', 'some', 'most', 'many', 'much', 'few', 'little', 'more', 'most', 'less',
            'very', 'quite', 'rather', 'too', 'enough', 'just', 'even', 'still', 'already', 'yet', 'again',
            'here', 'there', 'where', 'when', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose'
        }
    
    def _initialize_patterns(self):
        """Initialize regex patterns for text processing."""
        # Tech patterns
        self.tech_patterns = [
            r'\b[A-Z]{2,}\b',  # Acronyms (2+ uppercase letters)
            r'\b\w+\.js\b',    # JavaScript frameworks
            r'\b\w+\.py\b',    # Python files
            r'\b\w+\.net\b',   # .NET
            r'\b\w+\.io\b',    # .io services
        ]
        
        # Skill patterns
        self.skill_patterns = [
            r'\b\w+\s+development\b',
            r'\b\w+\s+engineering\b',
            r'\b\w+\s+programming\b',
            r'\b\w+\s+analysis\b',
            r'\b\w+\s+design\b',
            r'\b\w+\s+management\b',
        ]
        
        # Fluff words to remove
        self.fluff_words = {
            'ensure', 'ability', 'responsibility', 'through', 'via', 'read', 'ready', 'end',
            'ensure', 'ensure', 'ensure', 'ensure', 'ensure', 'ensure', 'ensure', 'ensure',
            'ability', 'ability', 'ability', 'ability', 'ability', 'ability', 'ability',
            'responsibility', 'responsibility', 'responsibility', 'responsibility',
            'through', 'through', 'through', 'through', 'through', 'through',
            'via', 'via', 'via', 'via', 'via', 'via', 'via', 'via',
            'read', 'read', 'read', 'read', 'read', 'read', 'read', 'read',
            'ready', 'ready', 'ready', 'ready', 'ready', 'ready', 'ready',
            'end', 'end', 'end', 'end', 'end', 'end', 'end', 'end'
        }
        
        # Months to remove
        self.months = {
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december',
            'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
        }
        
        # Tool/stack names to keep
        self.tool_names = {
            'figma', 'jira', 'notion', 'react', 'vue', 'angular', 'node', 'django', 'flask',
            'spring', 'express', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'kafka', 'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab',
            'aws', 'azure', 'gcp', 'terraform', 'ansible', 'python', 'javascript', 'java',
            'typescript', 'go', 'rust', 'swift', 'kotlin', 'html', 'css', 'sql', 'nosql'
        }
        
        # Acronyms to keep
        self.keep_acronyms = {'ux', 'ui', 'api', 'okr', 'kpi', 'crm', 'erp', 'saas', 'paas', 'iaas'}
    
    def normalize_text(self, text: str) -> str:
        """Enhanced text normalization."""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters (keep alphanumeric, spaces, hyphens)
        text = re.sub(r'[^\w\s\-]', ' ', text)
        
        # De-hyphenate (end-to-end -> end to end)
        text = re.sub(r'(\w)-(\w)', r'\1 \2', text)
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_tokens_and_phrases(self, text: str) -> List[str]:
        """Extract tokens and n-grams with improved tokenization."""
        if NLTK_AVAILABLE:
            try:
                tokens = word_tokenize(text)
            except:
                tokens = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]*\b', text.lower())
        else:
            tokens = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]*\b', text.lower())
        
        # Extract n-grams (1, 2, 3)
        all_tokens = list(tokens)
        
        # Add bigrams
        for i in range(len(tokens) - 1):
            bigram = ' '.join(tokens[i:i+2])
            if self._is_meaningful_phrase(bigram):
                all_tokens.append(bigram)
        
        # Add trigrams
        for i in range(len(tokens) - 2):
            trigram = ' '.join(tokens[i:i+3])
            if self._is_meaningful_phrase(trigram):
                all_tokens.append(trigram)
        
        return all_tokens
    
    def _is_meaningful_phrase(self, phrase: str) -> bool:
        """Check if a phrase is meaningful and not just common word combinations."""
        words = phrase.split()
        if len(words) > 3:
            return False
        
        # Skip common word combinations
        common_combinations = {
            ('we', 'are'), ('are', 'looking'), ('looking', 'for'), ('for', 'a'), ('for', 'the'),
            ('in', 'the'), ('of', 'the'), ('to', 'the'), ('with', 'the'), ('from', 'the'),
            ('at', 'the'), ('on', 'the'), ('by', 'the'), ('is', 'a'), ('is', 'the'),
            ('will', 'be'), ('can', 'be'), ('should', 'be'), ('must', 'be'), ('have', 'a'),
            ('has', 'a'), ('had', 'a'), ('get', 'a'), ('make', 'a'), ('take', 'a'),
            ('give', 'a'), ('put', 'a'), ('set', 'a'), ('go', 'to'), ('come', 'to'),
            ('look', 'at'), ('work', 'on'), ('work', 'with'), ('work', 'in'), ('work', 'for'),
            ('team', 'of'), ('part', 'of'), ('kind', 'of'), ('sort', 'of'), ('type', 'of'),
            ('lot', 'of'), ('bit', 'of'), ('piece', 'of'), ('number', 'of'), ('group', 'of'),
            ('set', 'of'), ('series', 'of'), ('pair', 'of'), ('couple', 'of'), ('handful', 'of')
        }
        
        if len(words) == 2 and (words[0], words[1]) in common_combinations:
            return False
        
        # Keep meaningful combinations
        meaningful_patterns = [
            # Tech terms
            ('user', 'experience'), ('user', 'interface'), ('user', 'research'),
            ('data', 'analysis'), ('data', 'science'), ('data', 'engineering'),
            ('machine', 'learning'), ('artificial', 'intelligence'), ('deep', 'learning'),
            ('web', 'development'), ('mobile', 'development'), ('front', 'end'),
            ('back', 'end'), ('full', 'stack'), ('software', 'engineering'),
            ('product', 'management'), ('project', 'management'), ('agile', 'development'),
            ('test', 'driven'), ('continuous', 'integration'), ('version', 'control'),
            # Business terms
            ('business', 'analysis'), ('business', 'intelligence'), ('business', 'development'),
            ('customer', 'experience'), ('customer', 'service'), ('customer', 'success'),
            ('market', 'research'), ('market', 'analysis'), ('competitive', 'analysis'),
            ('financial', 'analysis'), ('risk', 'management'), ('quality', 'assurance'),
            # Design terms
            ('graphic', 'design'), ('visual', 'design'), ('interaction', 'design'),
            ('information', 'architecture'), ('content', 'strategy'), ('brand', 'strategy'),
            # Operations terms
            ('operations', 'management'), ('supply', 'chain'), ('logistics', 'management'),
            ('human', 'resources'), ('talent', 'acquisition'), ('performance', 'management')
        ]
        
        if len(words) == 2 and (words[0], words[1]) in meaningful_patterns:
            return True
        
        # Keep if both words are meaningful (not common stop words)
        common_words = self.english_stopwords
        if len(words) == 2 and words[0] not in common_words and words[1] not in common_words:
            return True
        
        return False
    
    def apply_quality_filters(self, tokens: List[str]) -> List[str]:
        """Apply enhanced quality filters."""
        filtered_tokens = []
        
        for token in tokens:
            token_lower = token.lower()
            
            # Skip if in blacklist
            if token_lower in self.blacklist:
                continue
            
            # Skip if in HR stopwords
            if token_lower in self.hr_stopwords:
                continue
            
            # Skip common English stop words
            if token_lower in self.english_stopwords:
                continue
            
            # Skip fluff words
            if token_lower in self.fluff_words:
                continue
            
            # Skip months
            if token_lower in self.months:
                continue
            
            # Skip very short tokens (unless acronym/tool)
            if len(token) < 3 and not any(acronym in token.upper() for acronym in self.tech_whitelist):
                continue
            
            # Skip very long tokens (likely malformed)
            if len(token) > 50:
                continue
            
            # Skip n-grams that start or end with stop words
            if ' ' in token:
                words = token.split()
                if (words[0].lower() in self.english_stopwords or 
                    words[-1].lower() in self.english_stopwords or
                    any(word.lower() in self.english_stopwords for word in words)):
                    continue
            
            # Keep tech acronyms
            if any(acronym in token.upper() for acronym in self.tech_whitelist):
                filtered_tokens.append(token)
                continue
            
            # Keep tool names
            if token_lower in self.tool_names:
                filtered_tokens.append(token)
                continue
            
            # Keep important acronyms
            if token_lower in self.keep_acronyms:
                filtered_tokens.append(token)
                continue
            
            # Keep multi-word phrases that don't contain stop words
            if ' ' in token and len(token.split()) >= 2:
                filtered_tokens.append(token)
                continue
            
            # Keep tokens that look like skills/tools
            if self._looks_like_skill(token):
                filtered_tokens.append(token)
                continue
        
        return filtered_tokens
    
    def _looks_like_skill(self, token: str) -> bool:
        """Check if a token looks like a skill or tool."""
        # Check against tech patterns
        for pattern in self.tech_patterns:
            if re.search(pattern, token, re.IGNORECASE):
                return True
        
        # Check against skill patterns
        for pattern in self.skill_patterns:
            if re.search(pattern, token, re.IGNORECASE):
                return True
        
        # Check if it's in tech whitelist
        if any(tech_term.lower() in token.lower() for tech_term in self.tech_whitelist):
            return True
        
        return False
    
    def calculate_tfidf_scores(self, tokens: List[str], text: str) -> List[Tuple[str, float]]:
        """Calculate TF-IDF scores for tokens."""
        if not SKLEARN_AVAILABLE or not tokens:
            # Fallback to simple frequency scoring
            return self._simple_frequency_scoring(tokens, text)
        
        try:
            # Create document for TF-IDF
            doc_text = ' '.join(tokens)
            
            # Fit TF-IDF vectorizer
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([doc_text])
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Create token-score pairs
            token_scores = []
            for i, score in enumerate(tfidf_scores):
                if score > 0:
                    token_scores.append((feature_names[i], score))
            
            # Sort by score
            token_scores.sort(key=lambda x: x[1], reverse=True)
            return token_scores
            
        except Exception as e:
            logger.warning(f"TF-IDF calculation failed: {e}")
            return self._simple_frequency_scoring(tokens, text)
    
    def _simple_frequency_scoring(self, tokens: List[str], text: str) -> List[Tuple[str, float]]:
        """Fallback simple frequency scoring."""
        token_counts = Counter(tokens)
        scored_tokens = []
        
        for token, count in token_counts.items():
            score = count
            
            # Boost single words
            if ' ' not in token:
                score += 3
            else:
                score += 1
            
            # Boost tech terms
            if any(tech_term.lower() in token.lower() for tech_term in self.tech_whitelist):
                score += 3
            
            # Boost acronyms
            if re.match(r'^[A-Z]{2,}$', token):
                score += 2
            
            # Boost common tech patterns
            if self._looks_like_skill(token):
                score += 1
            
            scored_tokens.append((token, score))
        
        # Sort by score
        scored_tokens.sort(key=lambda x: x[1], reverse=True)
        return scored_tokens
    
    def apply_ranking_boosts(self, token_scores: List[Tuple[str, float]], text: str) -> List[Tuple[str, float]]:
        """Apply ranking boosts based on context."""
        boosted_scores = []
        
        for token, score in token_scores:
            boosted_score = score
            
            # Boost tool/stack names
            if token.lower() in self.tool_names:
                boosted_score *= 1.5
            
            # Boost acronyms
            if re.match(r'^[A-Z]{2,}$', token):
                boosted_score *= 1.3
            
            # Boost if occurs in bullet/heading lines
            lines = text.split('\n')
            for line in lines:
                if token.lower() in line.lower() and ('•' in line or '-' in line or line.strip().endswith(':')):
                    boosted_score *= 1.2
                    break
            
            # Boost noun-chunks (if SpaCy available)
            if self.nlp and ' ' not in token:
                try:
                    doc = self.nlp(token)
                    if doc and len(doc) == 1 and doc[0].pos_ in ['NOUN', 'PROPN']:
                        boosted_score *= 1.1
                except:
                    pass
            
            # Penalize very short tokens unless they're acronyms
            if len(token) < 3 and not re.match(r'^[A-Z]{2,}$', token):
                boosted_score *= 0.5
            
            boosted_scores.append((token, boosted_score))
        
        # Sort by boosted score
        boosted_scores.sort(key=lambda x: x[1], reverse=True)
        return boosted_scores
    
    def deduplicate_by_lemma(self, token_scores: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """Deduplicate tokens by lemma (designer/designers -> designer)."""
        if not self.stemmer:
            return token_scores
        
        seen_lemmas = set()
        deduplicated = []
        
        for token, score in token_scores:
            # Get lemma
            if ' ' in token:
                # For phrases, use the first word's lemma
                first_word = token.split()[0]
                lemma = self.stemmer.stem(first_word) if self.stemmer else first_word
            else:
                lemma = self.stemmer.stem(token) if self.stemmer else token
            
            if lemma not in seen_lemmas:
                seen_lemmas.add(lemma)
                deduplicated.append((token, score))
        
        return deduplicated
    
    def extract_enhanced_keywords(self, job_description: str, max_keywords: int = 30) -> List[str]:
        """Main method to extract enhanced keywords from job description."""
        if not job_description or not job_description.strip():
            return []
        
        # Create cache key
        cache_key = hashlib.md5(job_description.encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Step 1: Normalize text
            normalized_text = self.normalize_text(job_description)
            
            # Step 2: Extract tokens and phrases
            tokens = self.extract_tokens_and_phrases(normalized_text)
            
            # Step 3: Apply quality filters
            filtered_tokens = self.apply_quality_filters(tokens)
            
            # Step 4: Calculate TF-IDF scores
            token_scores = self.calculate_tfidf_scores(filtered_tokens, job_description)
            
            # Step 5: Apply ranking boosts
            boosted_scores = self.apply_ranking_boosts(token_scores, job_description)
            
            # Step 6: Deduplicate by lemma
            deduplicated_scores = self.deduplicate_by_lemma(boosted_scores)
            
            # Step 7: Get top keywords
            top_keywords = [token for token, score in deduplicated_scores[:max_keywords]]
            
            # Cache result
            self.cache[cache_key] = top_keywords
            
            logger.info(f"Extracted {len(top_keywords)} enhanced keywords")
            return top_keywords
            
        except Exception as e:
            logger.error(f"Error in enhanced keyword extraction: {e}")
            return []
    
    def find_matching_keywords_fuzzy(self, resume_text: str, jd_keywords: List[str]) -> Tuple[List[str], List[str]]:
        """Find matching keywords with fuzzy matching."""
        if not resume_text or not jd_keywords:
            return [], jd_keywords
        
        # Normalize resume text
        normalized_resume = self.normalize_text(resume_text)
        
        # Extract resume tokens
        resume_tokens = set(self.extract_tokens_and_phrases(normalized_resume))
        
        # Find matches
        matched_keywords = []
        missing_keywords = []
        
        for keyword in jd_keywords:
            keyword_lower = keyword.lower()
            
            # Check exact match
            if keyword_lower in resume_tokens:
                matched_keywords.append(keyword)
                continue
            
            # Check if all parts of multi-word keyword are present
            if ' ' in keyword:
                parts = keyword.split()
                if all(part.lower() in resume_tokens for part in parts):
                    matched_keywords.append(keyword)
                    continue
            
            # Fuzzy matching with RapidFuzz
            if RAPIDFUZZ_AVAILABLE:
                best_match = process.extractOne(keyword, list(resume_tokens), scorer=fuzz.token_set_ratio)
                if best_match and best_match[1] >= 90:  # 90% similarity threshold
                    matched_keywords.append(keyword)
                    continue
            
            # Check synonyms
            found_synonym = False
            for canonical, variants in self.synonyms.items():
                if keyword_lower == canonical.lower() or keyword_lower in [v.lower() for v in variants]:
                    # Check if any synonym is in resume
                    for variant in variants:
                        if variant.lower() in resume_tokens:
                            matched_keywords.append(keyword)
                            found_synonym = True
                            break
                    if found_synonym:
                        break
            
            if not found_synonym:
                missing_keywords.append(keyword)
        
        return matched_keywords, missing_keywords
    
    def calculate_enhanced_scores(self, matched_keywords: List[str], all_keywords: List[str], 
                                resume_text: str, jd_text: str) -> Dict[str, float]:
        """Calculate enhanced scores with semantic similarity option."""
        if not all_keywords:
            return {"score": 0, "similarity": 0, "coverage": 0}
        
        # Coverage percentage
        coverage = len(matched_keywords) / max(len(all_keywords), 1)
        coverage_pct = coverage * 100
        
        # Similarity calculation
        if self.semantic_on and SKLEARN_AVAILABLE:
            # Use TF-IDF cosine similarity
            try:
                vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
                tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
                similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
                similarity = similarity_matrix[0][0] * 100
            except Exception as e:
                logger.warning(f"Semantic similarity calculation failed: {e}")
                similarity = self._calculate_simple_similarity(resume_text, jd_text)
        else:
            similarity = self._calculate_simple_similarity(resume_text, jd_text)
        
        # Overall score
        score = round(similarity * 0.6 + coverage_pct * 0.4)
        score = max(0, min(100, score))  # Clamp to 0-100
        
        return {
            "score": score,
            "similarity": round(similarity, 1),
            "coverage": round(coverage_pct, 1)
        }
    
    def _calculate_simple_similarity(self, resume_text: str, jd_text: str) -> float:
        """Calculate simple word overlap similarity."""
        resume_words = set(self.normalize_text(resume_text).split())
        jd_words = set(self.normalize_text(jd_text).split())
        
        if not jd_words:
            return 0
        
        common_words = resume_words.intersection(jd_words)
        similarity = len(common_words) / len(jd_words) * 100
        return similarity
    
    def generate_enhanced_bullet_suggestions(self, missing_keywords: List[str], max_suggestions: int = 10) -> List[str]:
        """Generate enhanced bullet suggestions with templates."""
        if not missing_keywords:
            return []
        
        # Action verbs organized by category
        action_verbs = {
            "leadership": ["Led", "Directed", "Championed", "Spearheaded", "Orchestrated", "Pioneered"],
            "creation": ["Designed", "Developed", "Created", "Built", "Crafted", "Architected", "Engineered"],
            "optimization": ["Optimized", "Enhanced", "Improved", "Streamlined", "Refined", "Accelerated"],
            "implementation": ["Implemented", "Deployed", "Executed", "Delivered", "Launched", "Rolled out"],
            "analysis": ["Conducted", "Analyzed", "Evaluated", "Assessed", "Investigated", "Researched"],
            "management": ["Managed", "Coordinated", "Facilitated", "Oversaw", "Supervised", "Governed"],
            "collaboration": ["Collaborated", "Partnered", "Aligned", "Integrated", "Unified", "Synchronized"],
            "innovation": ["Innovated", "Transformed", "Revolutionized", "Modernized", "Evolved", "Advanced"]
        }
        
        # Template patterns
        templates = [
            "Drove <metric> by <action> using <keyword>, resulting in <impact>",
            "Established <process> with <keyword> to reduce <waste> and improve <metric>",
            "Adopted <keyword> in the design workflow to <benefit>, cutting <time> by <X%>",
            "Led <method> with <n> participants to validate <hypothesis>, informing <decision> using <keyword>",
            "Built a reusable <keyword> library to speed delivery by <X%>",
            "Implemented <keyword> solution that increased <metric> by <X%>",
            "Designed <system> using <keyword> to optimize <process> and reduce <cost>",
            "Developed <strategy> leveraging <keyword> to enhance <outcome> and improve <metric>"
        ]
        
        suggestions = []
        used_verbs = set()
        
        for i, keyword in enumerate(missing_keywords[:max_suggestions]):
            # Select action verb category based on keyword type
            if any(tech in keyword.lower() for tech in ['design', 'ui', 'ux', 'visual', 'graphic']):
                verb_category = "creation"
            elif any(tech in keyword.lower() for tech in ['manage', 'lead', 'direct', 'supervise']):
                verb_category = "leadership"
            elif any(tech in keyword.lower() for tech in ['optimize', 'improve', 'enhance', 'streamline']):
                verb_category = "optimization"
            elif any(tech in keyword.lower() for tech in ['implement', 'deploy', 'execute', 'deliver']):
                verb_category = "implementation"
            elif any(tech in keyword.lower() for tech in ['analyze', 'research', 'evaluate', 'assess']):
                verb_category = "analysis"
            else:
                verb_category = "creation"  # Default
            
            # Select verb (avoid repetition)
            available_verbs = [v for v in action_verbs[verb_category] if v not in used_verbs]
            if not available_verbs:
                available_verbs = action_verbs[verb_category]
            
            verb = available_verbs[i % len(available_verbs)]
            used_verbs.add(verb)
            
            # Select template
            template = templates[i % len(templates)]
            
            # Generate suggestion
            suggestion = template.replace('<keyword>', keyword)
            suggestion = suggestion.replace('<action>', f"{verb.lower()}ing")
            suggestion = suggestion.replace('<metric>', "performance metrics")
            suggestion = suggestion.replace('<impact>', "significant improvements")
            suggestion = suggestion.replace('<process>', "efficient processes")
            suggestion = suggestion.replace('<waste>', "operational waste")
            suggestion = suggestion.replace('<benefit>', "enhance productivity")
            suggestion = suggestion.replace('<time>', "processing time")
            suggestion = suggestion.replace('<X%>', "25%")
            suggestion = suggestion.replace('<method>', "user research")
            suggestion = suggestion.replace('<n>', "50+")
            suggestion = suggestion.replace('<hypothesis>', "design assumptions")
            suggestion = suggestion.replace('<decision>', "product decisions")
            suggestion = suggestion.replace('<system>', "comprehensive system")
            suggestion = suggestion.replace('<cost>', "operational costs")
            suggestion = suggestion.replace('<strategy>', "data-driven strategy")
            suggestion = suggestion.replace('<outcome>', "user experience")
            
            suggestions.append(suggestion)
        
        return suggestions[:max_suggestions]

