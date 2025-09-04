"""
Smart JD Keyword Extraction & Filtering System

This module implements a comprehensive NLP pipeline for extracting high-quality
keywords from job descriptions, filtering out noise and HR filler content.
"""

import re
import json
import logging
import unicodedata
from typing import List, Dict, Set, Tuple, Any, Optional
from collections import Counter, defaultdict
from pathlib import Path
import hashlib

# NLP libraries
import spacy
import yake
from rake_nltk import Rake
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import wordfreq
from rapidfuzz import fuzz
import symspellpy
from symspellpy import SymSpell, Verbosity

logger = logging.getLogger(__name__)

class SmartKeywordExtractor:
    """
    Advanced keyword extraction with multi-layer filtering and ranking.
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.cache = {}
        
        # Load data files
        self._load_data_files()
        
        # Initialize NLP models
        self._initialize_models()
        
        # Initialize SymSpell for typo correction
        self._initialize_symspell()
    
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
    
    def _initialize_models(self):
        """Initialize spaCy and other NLP models."""
        try:
            # Load spaCy model (try different models)
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                try:
                    self.nlp = spacy.load("en_core_web_md")
                except OSError:
                    logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
                    self.nlp = None
            
            # Initialize YAKE
            self.yake_extractor = yake.KeywordExtractor(
                lan="en",
                n=3,  # max n-gram size
                dedupLim=0.7,
                top=100,
                features=None
            )
            
            # Initialize RAKE
            self.rake_extractor = Rake(
                min_length=1,
                max_length=3,
                include_repeated_phrases=False
            )
            
            # Initialize TF-IDF
            self.tfidf_vectorizer = TfidfVectorizer(
                ngram_range=(1, 3),
                max_features=1000,
                stop_words='english',
                lowercase=True,
                token_pattern=r'\b[a-zA-Z][a-zA-Z0-9]*\b'
            )
            
            logger.info("NLP models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing NLP models: {e}")
            self.nlp = None
            self.yake_extractor = None
            self.rake_extractor = None
            self.tfidf_vectorizer = None
    
    def _initialize_symspell(self):
        """Initialize SymSpell for typo correction."""
        try:
            self.sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
            # Load a basic dictionary (you can expand this)
            dictionary_path = "frequency_dictionary_en_82_765.txt"
            if Path(dictionary_path).exists():
                self.sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
            else:
                # Create a minimal dictionary with common tech terms
                tech_terms = list(self.tech_whitelist) + list(self.synonyms.keys())
                for term in tech_terms:
                    self.sym_spell.create_dictionary_entry(term.lower(), 1)
            
            logger.info("SymSpell initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing SymSpell: {e}")
            self.sym_spell = None
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text: lowercase, unicode normalize, strip punctuation/emoji, de-hyphenate.
        """
        if not text:
            return ""
        
        # Unicode normalization
        text = unicodedata.normalize('NFKD', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove emojis and special characters (keep alphanumeric, spaces, hyphens)
        text = re.sub(r'[^\w\s\-]', ' ', text)
        
        # De-hyphenate (end-to-end -> end to end)
        text = re.sub(r'(\w)-(\w)', r'\1 \2', text)
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_tokens_and_phrases(self, text: str) -> List[str]:
        """
        Extract tokens and n-grams from normalized text.
        """
        if not self.nlp:
            # Fallback: simple tokenization
            tokens = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]*\b', text.lower())
            return tokens
        
        doc = self.nlp(text)
        tokens = []
        
        # Extract individual tokens
        for token in doc:
            if not token.is_space and not token.is_punct:
                tokens.append(token.text.lower())
        
        # Extract n-grams (2-3 words)
        for n in [2, 3]:
            for i in range(len(tokens) - n + 1):
                ngram = ' '.join(tokens[i:i+n])
                tokens.append(ngram)
        
        return tokens
    
    def apply_pos_ner_filters(self, tokens: List[str]) -> List[str]:
        """
        Apply POS and NER filtering to keep only relevant tokens.
        """
        if not self.nlp or not tokens:
            return tokens
        
        filtered_tokens = []
        
        for token in tokens:
            # For n-grams, check the first word's POS
            first_word = token.split()[0] if ' ' in token else token
            
            try:
                doc = self.nlp(first_word)
                if not doc:
                    continue
                
                token_obj = doc[0]
                
                # Keep nouns, proper nouns, adjectives
                if token_obj.pos_ in ['NOUN', 'PROPN', 'ADJ']:
                    filtered_tokens.append(token)
                # Allow some specific verbs (white-listed)
                elif token_obj.pos_ == 'VERB' and token in ['prototype', 'mentor', 'lead', 'manage', 'develop', 'design', 'implement', 'optimize', 'analyze', 'create', 'build']:
                    filtered_tokens.append(token)
                # Keep tech acronyms regardless of POS
                elif any(acronym in token.upper() for acronym in self.tech_whitelist):
                    filtered_tokens.append(token)
                    
            except Exception as e:
                logger.debug(f"Error processing token {token}: {e}")
                continue
        
        return filtered_tokens
    
    def apply_noise_suppression(self, tokens: List[str]) -> List[str]:
        """
        Apply multi-layer noise suppression filters.
        """
        filtered_tokens = []
        
        for token in tokens:
            # Skip if in blacklist
            if token.lower() in self.blacklist:
                continue
            
            # Skip if in HR stopwords
            if token.lower() in self.hr_stopwords:
                continue
            
            # Skip very short tokens (unless in tech whitelist)
            if len(token) < 3 and not any(acronym in token.upper() for acronym in self.tech_whitelist):
                continue
            
            # Skip if too generic (high frequency in general English)
            try:
                if len(token) > 3 and wordfreq.zipf_frequency(token, 'en') >= 6.0:
                    # Check if it's in our domain whitelist
                    if not any(tech_term.lower() in token.lower() for tech_term in self.tech_whitelist):
                        continue
            except:
                pass  # Skip frequency check if wordfreq fails
            
            # Apply typo correction
            corrected_token = self._correct_typos(token)
            if corrected_token:
                filtered_tokens.append(corrected_token)
        
        return filtered_tokens
    
    def _correct_typos(self, token: str) -> Optional[str]:
        """
        Correct obvious typos using SymSpell.
        """
        if not self.sym_spell:
            return token
        
        # Check if token is already correct
        if self.sym_spell.lookup(token, Verbosity.TOP, max_edit_distance=2):
            return token
        
        # Try to find suggestions
        suggestions = self.sym_spell.lookup(token, Verbosity.CLOSEST, max_edit_distance=2)
        
        if suggestions:
            # Use the best suggestion if confidence is high enough
            best_suggestion = suggestions[0]
            if best_suggestion.distance <= 1:  # Only accept 1-edit distance corrections
                return best_suggestion.term
        
        # If no good correction found, return original token
        return token
    
    def collapse_near_duplicates(self, tokens: List[str]) -> List[str]:
        """
        Collapse near-duplicates (e.g., "requirements" = "requirement").
        """
        # Group similar tokens
        groups = defaultdict(list)
        
        for token in tokens:
            # Find the best group for this token
            best_group = None
            best_similarity = 0
            
            for group_key in groups:
                similarity = fuzz.ratio(token.lower(), group_key.lower())
                if similarity > 80 and similarity > best_similarity:  # 80% similarity threshold
                    best_similarity = similarity
                    best_group = group_key
            
            if best_group:
                groups[best_group].append(token)
            else:
                groups[token].append(token)
        
        # Return the most common token from each group
        result = []
        for group_tokens in groups.values():
            # Use the shortest token as the canonical form
            canonical = min(group_tokens, key=len)
            result.append(canonical)
        
        return result
    
    def extract_keywords_yake_rake(self, text: str) -> List[Tuple[str, float]]:
        """
        Extract keywords using YAKE and RAKE, then combine results.
        """
        keywords = []
        
        # YAKE extraction
        if self.yake_extractor:
            try:
                yake_keywords = self.yake_extractor.extract_keywords(text)
                for keyword, score in yake_keywords:
                    keywords.append((keyword.lower(), 1.0 - score))  # Convert YAKE score to relevance
            except Exception as e:
                logger.debug(f"YAKE extraction failed: {e}")
        
        # RAKE extraction
        if self.rake_extractor:
            try:
                self.rake_extractor.extract_keywords_from_text(text)
                rake_keywords = self.rake_extractor.get_ranked_phrases_with_scores()
                for score, keyword in rake_keywords:
                    keywords.append((keyword.lower(), score))
            except Exception as e:
                logger.debug(f"RAKE extraction failed: {e}")
        
        return keywords
    
    def apply_tfidf_ranking(self, text: str, candidates: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """
        Re-rank candidates using TF-IDF against the whole JD.
        """
        if not candidates or not self.tfidf_vectorizer:
            return candidates
        
        try:
            # Create TF-IDF matrix
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text])
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            
            # Get TF-IDF scores for candidates
            candidate_scores = {}
            for candidate, base_score in candidates:
                if candidate in feature_names:
                    idx = list(feature_names).index(candidate)
                    tfidf_score = tfidf_matrix[0, idx]
                    candidate_scores[candidate] = float(tfidf_score)
                else:
                    candidate_scores[candidate] = 0.0
            
            # Combine base scores with TF-IDF scores
            ranked_candidates = []
            for candidate, base_score in candidates:
                tfidf_score = candidate_scores.get(candidate, 0.0)
                combined_score = base_score * 0.7 + tfidf_score * 0.3
                ranked_candidates.append((candidate, combined_score))
            
            # Sort by combined score
            ranked_candidates.sort(key=lambda x: x[1], reverse=True)
            return ranked_candidates
            
        except Exception as e:
            logger.debug(f"TF-IDF ranking failed: {e}")
            return candidates
    
    def apply_boosts_and_penalties(self, candidates: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """
        Apply boosts for multi-word phrases and tech terms, penalties for generic terms.
        """
        boosted_candidates = []
        
        for candidate, score in candidates:
            adjusted_score = score
            
            # Boost multi-word phrases
            if ' ' in candidate:
                adjusted_score += 0.15
            
            # Boost known tech terms
            candidate_upper = candidate.upper()
            if any(tech_term in candidate_upper for tech_term in self.tech_whitelist):
                adjusted_score += 0.25
            
            # Check synonyms for tech terms
            for canonical, variants in self.synonyms.items():
                if any(variant.lower() in candidate.lower() for variant in variants):
                    adjusted_score += 0.25
                    break
            
            # Penalize very generic single words
            if ' ' not in candidate and len(candidate) > 3:
                try:
                    if wordfreq.zipf_frequency(candidate, 'en') >= 5.5:
                        adjusted_score -= 0.2
                except:
                    pass
            
            boosted_candidates.append((candidate, max(0.0, adjusted_score)))
        
        return boosted_candidates
    
    def extract_smart_keywords(self, job_description: str, max_keywords: int = 30) -> List[str]:
        """
        Main method to extract smart keywords from job description.
        """
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
            
            # Step 3: Apply POS and NER filters
            filtered_tokens = self.apply_pos_ner_filters(tokens)
            
            # Step 4: Apply noise suppression
            clean_tokens = self.apply_noise_suppression(filtered_tokens)
            
            # Step 5: Collapse near-duplicates
            unique_tokens = self.collapse_near_duplicates(clean_tokens)
            
            # Step 6: Extract keywords using YAKE/RAKE
            keyword_candidates = self.extract_keywords_yake_rake(job_description)
            
            # Step 7: Apply TF-IDF ranking
            ranked_candidates = self.apply_tfidf_ranking(job_description, keyword_candidates)
            
            # Step 8: Apply boosts and penalties
            final_candidates = self.apply_boosts_and_penalties(ranked_candidates)
            
            # Step 9: Filter to only include tokens that passed our filters
            filtered_candidates = [
                (candidate, score) for candidate, score in final_candidates
                if candidate in unique_tokens or any(part in unique_tokens for part in candidate.split())
            ]
            
            # Step 10: Get top keywords
            top_keywords = [candidate for candidate, score in filtered_candidates[:max_keywords]]
            
            # Cache result
            self.cache[cache_key] = top_keywords
            
            logger.info(f"Extracted {len(top_keywords)} smart keywords")
            return top_keywords
            
        except Exception as e:
            logger.error(f"Error in smart keyword extraction: {e}")
            return []
    
    def find_matching_keywords(self, resume_text: str, jd_keywords: List[str]) -> Tuple[List[str], List[str]]:
        """
        Find which JD keywords are present in the resume.
        """
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


