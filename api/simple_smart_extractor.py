"""
Simplified Smart Keyword Extractor - Works without external dependencies
This is a fallback implementation that provides basic smart filtering.
"""

import re
import json
import logging
from typing import List, Dict, Set, Tuple, Optional
from collections import Counter, defaultdict
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

class SimpleSmartExtractor:
    """
    Simplified smart keyword extractor that works without external NLP dependencies.
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.cache = {}
        
        # Load data files
        self._load_data_files()
        
        # Initialize basic patterns
        self._initialize_patterns()
    
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
    
    def _initialize_patterns(self):
        """Initialize regex patterns for text processing."""
        # Common tech patterns
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
    
    def normalize_text(self, text: str) -> str:
        """Normalize text: lowercase, strip punctuation, de-hyphenate."""
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
        """Extract tokens and limited n-grams from normalized text."""
        # Simple tokenization
        tokens = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]*\b', text.lower())
        
        # Extract limited n-grams (only 2-word phrases, and only for meaningful combinations)
        for i in range(len(tokens) - 1):
            ngram = ' '.join(tokens[i:i+2])
            # Only add n-grams that look like meaningful terms
            if self._is_meaningful_phrase(ngram):
                tokens.append(ngram)
        
        return tokens
    
    def _is_meaningful_phrase(self, phrase: str) -> bool:
        """Check if a 2-word phrase is meaningful and not just common word combinations."""
        words = phrase.split()
        if len(words) != 2:
            return False
        
        word1, word2 = words
        
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
        
        if (word1, word2) in common_combinations:
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
        
        if (word1, word2) in meaningful_patterns:
            return True
        
        # Keep if both words are meaningful (not common stop words)
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'}
        
        if word1 not in common_words and word2 not in common_words:
            return True
        
        return False
    
    def apply_basic_filters(self, tokens: List[str]) -> List[str]:
        """Apply basic filtering without NLP dependencies."""
        filtered_tokens = []
        
        # Common English stop words that should be filtered out
        common_stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in', 'is', 'it', 'its',
            'of', 'on', 'that', 'the', 'to', 'was', 'will', 'with', 'you', 'your', 'we', 'our', 'they', 'them',
            'this', 'these', 'those', 'i', 'me', 'my', 'us', 'him', 'her', 'his', 'hers', 'their', 'theirs',
            'am', 'are', 'is', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
            'did', 'doing', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall',
            'if', 'or', 'but', 'so', 'yet', 'nor', 'for', 'and', 'not', 'only', 'also', 'either', 'neither',
            'both', 'all', 'any', 'some', 'most', 'many', 'much', 'few', 'little', 'more', 'most', 'less',
            'very', 'quite', 'rather', 'too', 'enough', 'just', 'even', 'still', 'already', 'yet', 'again',
            'here', 'there', 'where', 'when', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose',
            're', 'll', 've', 'd', 's', 't', 'm', 'nt', 'aren', 'isn', 'wasn', 'weren', 'haven', 'hasn',
            'hadn', 'don', 'doesn', 'didn', 'won', 'wouldn', 'couldn', 'shouldn', 'can', 'cant',
            # Additional generic words to filter out
            'remote', 'europe', 'future', 'rich', 'premium', 'hiring', 'hire', 'working', 'works', 'teams',
            'experience', 'experice', 'great', 'better', 'about', 'other', 'good', 'best', 'new', 'old',
            'work', 'looking', 'position', 'role', 'job', 'career', 'opportunity', 'company', 'organization',
            'big', 'small', 'large', 'little', 'high', 'low', 'fast', 'slow', 'easy', 'hard', 'simple',
            'complex', 'important', 'main', 'major', 'minor', 'different', 'same', 'similar', 'various',
            'several', 'multiple', 'single', 'double', 'triple', 'first', 'last', 'next', 'previous',
            'current', 'recent', 'latest', 'early', 'late', 'long', 'short', 'wide', 'narrow', 'deep',
            'shallow', 'thick', 'thin', 'heavy', 'light', 'strong', 'weak', 'powerful', 'effective',
            'efficient', 'successful', 'popular', 'famous', 'known', 'unknown', 'public', 'private',
            'open', 'closed', 'free', 'paid', 'available', 'unavailable', 'possible', 'impossible',
            'necessary', 'optional', 'required', 'recommended', 'suggested', 'preferred', 'ideal',
            'perfect', 'excellent', 'outstanding', 'amazing', 'wonderful', 'fantastic', 'incredible',
            'awesome', 'terrible', 'awful', 'bad', 'worse', 'worst', 'horrible', 'disgusting',
            'beautiful', 'ugly', 'pretty', 'handsome', 'attractive', 'unattractive', 'interesting',
            'boring', 'exciting', 'fun', 'funny', 'serious', 'formal', 'casual', 'professional',
            'personal', 'business', 'commercial', 'industrial', 'academic', 'educational', 'medical',
            'legal', 'financial', 'technical', 'creative', 'artistic', 'scientific', 'practical',
            'theoretical', 'basic', 'advanced', 'beginner', 'intermediate', 'expert', 'professional',
            'amateur', 'experienced', 'inexperienced', 'skilled', 'unskilled', 'talented', 'gifted',
            'intelligent', 'smart', 'clever', 'wise', 'foolish', 'stupid', 'dumb', 'brilliant',
            'genius', 'creative', 'innovative', 'original', 'unique', 'special', 'ordinary', 'normal',
            'typical', 'standard', 'common', 'rare', 'unusual', 'strange', 'weird', 'odd', 'different'
        }
        
        for token in tokens:
            # Skip if in blacklist
            if token.lower() in self.blacklist:
                continue
            
            # Skip if in HR stopwords
            if token.lower() in self.hr_stopwords:
                continue
            
            # Skip common English stop words
            if token.lower() in common_stopwords:
                continue
            
            # Skip very short tokens (unless in tech whitelist)
            if len(token) < 3 and not any(acronym in token.upper() for acronym in self.tech_whitelist):
                continue
            
            # Skip very long tokens (likely malformed)
            if len(token) > 50:
                continue
            
            # Skip n-grams that start or end with stop words
            if ' ' in token:
                words = token.split()
                if (words[0].lower() in common_stopwords or 
                    words[-1].lower() in common_stopwords or
                    any(word.lower() in common_stopwords for word in words)):
                    continue
            
            # Keep tech acronyms
            if any(acronym in token.upper() for acronym in self.tech_whitelist):
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
        
        # Check if it's a common programming language or tool
        common_tech = {
            'python', 'javascript', 'java', 'typescript', 'go', 'rust', 'swift', 'kotlin',
            'react', 'vue', 'angular', 'node', 'django', 'flask', 'spring', 'express',
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'kafka',
            'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab',
            'aws', 'azure', 'gcp', 'terraform', 'ansible'
        }
        
        return token.lower() in common_tech
    
    def simple_ranking(self, tokens: List[str], text: str) -> List[Tuple[str, float]]:
        """Simple ranking based on frequency and patterns, prioritizing single words."""
        # Count frequency
        token_counts = Counter(tokens)
        
        # Calculate scores and track seen words to avoid duplicates
        scored_tokens = []
        seen_words = set()
        
        for token, count in token_counts.items():
            # Skip if we've already seen this word in a different form
            token_words = set(token.lower().split())
            if any(word in seen_words for word in token_words):
                continue
            
            score = count
            
            # Prioritize single words over phrases
            if ' ' not in token:
                score += 3  # Strong boost for single words
            else:
                score += 1  # Smaller boost for phrases
            
            # Boost tech terms
            if any(tech_term.lower() in token.lower() for tech_term in self.tech_whitelist):
                score += 3
            
            # Boost acronyms
            if re.match(r'^[A-Z]{2,}$', token):
                score += 2
            
            # Boost common tech patterns
            if self._looks_like_skill(token):
                score += 1
            
            # Add words to seen set
            seen_words.update(token_words)
            scored_tokens.append((token, score))
        
        # Sort by score
        scored_tokens.sort(key=lambda x: x[1], reverse=True)
        return scored_tokens
    
    def extract_smart_keywords(self, job_description: str, max_keywords: int = 30) -> List[str]:
        """Main method to extract smart keywords from job description."""
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
            
            # Step 3: Apply basic filters
            filtered_tokens = self.apply_basic_filters(tokens)
            
            # Step 4: Simple ranking
            ranked_tokens = self.simple_ranking(filtered_tokens, job_description)
            
            # Step 5: Get top keywords
            top_keywords = [token for token, score in ranked_tokens[:max_keywords]]
            
            # Cache result
            self.cache[cache_key] = top_keywords
            
            logger.info(f"Extracted {len(top_keywords)} smart keywords (simple mode)")
            return top_keywords
            
        except Exception as e:
            logger.error(f"Error in simple smart keyword extraction: {e}")
            return []
    
    def find_matching_keywords(self, resume_text: str, jd_keywords: List[str]) -> Tuple[List[str], List[str]]:
        """Find which JD keywords are present in the resume."""
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
            # Check exact match
            if keyword.lower() in resume_tokens:
                matched_keywords.append(keyword)
                continue
            
            # Check if all parts of multi-word keyword are present
            if ' ' in keyword:
                parts = keyword.split()
                if all(part.lower() in resume_tokens for part in parts):
                    matched_keywords.append(keyword)
                    continue
            
            # Check synonyms
            keyword_lower = keyword.lower()
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
