"""
Deterministic locks for blocking Figma-fragmented PDFs
"""
import hashlib
import logging
import os
import re
from typing import Dict, List, Set, Tuple, Optional
import json

logger = logging.getLogger(__name__)

# English wordlist for dictionary coverage lock
COMMON_WORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with',
    'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her',
    'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up',
    'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time',
    'no', 'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could',
    'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think',
    'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even',
    'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us', 'is', 'was', 'are',
    'been', 'has', 'had', 'were', 'said', 'each', 'which', 'their', 'said', 'will', 'about', 'if',
    'up', 'out', 'many', 'then', 'them', 'can', 'only', 'other', 'new', 'some', 'what', 'time',
    'very', 'when', 'much', 'get', 'through', 'back', 'much', 'before', 'go', 'good', 'little',
    'very', 'still', 'should', 'home', 'big', 'give', 'air', 'well', 'large', 'must', 'big',
    'even', 'such', 'because', 'turn', 'here', 'why', 'ask', 'went', 'men', 'read', 'need',
    'land', 'different', 'home', 'us', 'move', 'try', 'kind', 'hand', 'picture', 'again',
    'change', 'off', 'play', 'spell', 'air', 'away', 'animal', 'house', 'point', 'page',
    'letter', 'mother', 'answer', 'found', 'study', 'still', 'learn', 'should', 'america',
    'world', 'high', 'every', 'near', 'add', 'food', 'between', 'own', 'below', 'country',
    'plant', 'last', 'school', 'father', 'keep', 'tree', 'never', 'start', 'city', 'earth',
    'eye', 'light', 'thought', 'head', 'under', 'story', 'saw', 'left', 'dont', 'few',
    'while', 'along', 'might', 'close', 'something', 'seemed', 'next', 'hard', 'open',
    'example', 'begin', 'life', 'always', 'those', 'both', 'paper', 'together', 'got',
    'group', 'often', 'run', 'important', 'until', 'children', 'side', 'feet', 'car',
    'miles', 'night', 'walked', 'white', 'sea', 'began', 'grew', 'took', 'river', 'four',
    'carry', 'state', 'once', 'book', 'hear', 'stop', 'without', 'second', 'later',
    'miss', 'idea', 'enough', 'eat', 'face', 'watch', 'far', 'indian', 'real', 'almost',
    'let', 'above', 'girl', 'sometimes', 'mountain', 'cut', 'young', 'talk', 'soon',
    'list', 'song', 'leave', 'family', 'it\'s', 'its', 'let\'s', 'that\'s', 'i\'m',
    'you\'re', 'we\'re', 'they\'re', 'i\'ve', 'you\'ve', 'we\'ve', 'they\'ve',
    'i\'ll', 'you\'ll', 'we\'ll', 'they\'ll', 'i\'d', 'you\'d', 'we\'d', 'they\'d',
    'don\'t', 'doesn\'t', 'didn\'t', 'won\'t', 'wouldn\'t', 'shouldn\'t', 'couldn\'t',
    'can\'t', 'isn\'t', 'aren\'t', 'wasn\'t', 'weren\'t', 'hasn\'t', 'haven\'t', 'hadn\'t'
}

# Character bigram probabilities for English (simplified)
BIGRAM_PROBS = {
    'th': 0.035, 'he': 0.030, 'in': 0.024, 'er': 0.020, 'an': 0.019, 're': 0.018,
    'nd': 0.017, 'on': 0.016, 'en': 0.015, 'at': 0.014, 'ou': 0.013, 'ed': 0.012,
    'ha': 0.011, 'to': 0.011, 'or': 0.010, 'it': 0.010, 'is': 0.009, 'hi': 0.009,
    'es': 0.009, 'ng': 0.008, 'of': 0.008, 'al': 0.008, 'de': 0.007, 'se': 0.007,
    'le': 0.007, 'sa': 0.007, 'si': 0.006, 'ar': 0.006, 've': 0.006, 'ra': 0.006,
    'ld': 0.006, 'ur': 0.006, 'lo': 0.005, 'wa': 0.005, 'll': 0.005, 'tt': 0.005,
    'ff': 0.004, 'ss': 0.004, 'ee': 0.004, 'oo': 0.004, 'ck': 0.004, 'gg': 0.003,
    'pp': 0.003, 'mm': 0.003, 'nn': 0.003, 'dd': 0.003, 'bb': 0.002, 'cc': 0.002,
    'rr': 0.002, 'aa': 0.001, 'ii': 0.001, 'uu': 0.001, 'yy': 0.001, 'zz': 0.001
}

# Fallback probability for unseen bigrams
EPSILON = 1e-6

class DeterministicLocks:
    """Deterministic locks for blocking fragmented PDFs"""
    
    def __init__(self):
        self.debug_mode = os.getenv('PREFLIGHT_DEBUG', '0') == '1'
        self.block_hashes = self._load_block_hashes()
        
    def _load_block_hashes(self) -> Set[str]:
        """Load hash kill-switch from environment"""
        hash_list = os.getenv('BLOCK_BY_HASH', '')
        if hash_list:
            return set(h.strip().lower() for h in hash_list.split(','))
        return set()
    
    def check_hash_killswitch(self, file_content: bytes) -> Optional[str]:
        """Check if file should be blocked by hash kill-switch"""
        try:
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            if self.debug_mode:
                logger.info(f"File hash (first 8): {file_hash[:8]}")
                logger.info(f"Block hashes: {self.block_hashes}")
            
            if file_hash in self.block_hashes:
                logger.info(f"Hash {file_hash[:8]} found in block list")
                return 'hash_kill_switch'
            
            logger.info(f"Hash {file_hash[:8]} not in block list")
            return None
        except Exception as e:
            logger.error(f"Error in check_hash_killswitch: {e}")
            return None
    
    def check_dictionary_coverage(self, text: str, total_chars: int) -> Tuple[bool, float]:
        """
        Dictionary coverage lock: fragmented PDFs yield broken tokens
        Returns (should_block, dict_hits_ratio)
        """
        if total_chars < 600:
            return False, 0.0
        
        # Extract tokens of length >= 4, alphabetic only
        tokens = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        if len(tokens) == 0:
            return True, 0.0  # No valid tokens = fragmented
        
        # Count dictionary hits
        dict_hits = sum(1 for token in tokens if token in COMMON_WORDS)
        dict_hits_ratio = dict_hits / len(tokens)
        
        if self.debug_mode:
            logger.info(f"Dictionary coverage: {dict_hits}/{len(tokens)} = {dict_hits_ratio:.3f}")
        
        # Block if < 5% of 4+ letter tokens are in dictionary (more lenient for good files)
        should_block = dict_hits_ratio < 0.05
        return should_block, dict_hits_ratio
    
    def check_bigram_perplexity(self, text: str, total_chars: int) -> Tuple[bool, float]:
        """
        Character bigram perplexity lock: fragmented text has unlikely transitions
        Returns (should_block, nll_per_char)
        """
        if total_chars < 600:
            return False, 0.0
        
        # Normalize text: lowercase, collapse whitespace, keep only [a-z ]
        normalized = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        if len(normalized) < 10:
            return True, 10.0  # Too short = fragmented
        
        # Compute bigram probabilities
        total_nll = 0.0
        bigram_count = 0
        
        for i in range(len(normalized) - 1):
            bigram = normalized[i:i+2]
            if bigram[0].isalpha() and bigram[1].isalpha():
                prob = BIGRAM_PROBS.get(bigram, EPSILON)
                total_nll += -1.0 * (prob if prob > 0 else EPSILON)
                bigram_count += 1
        
        if bigram_count == 0:
            return True, 10.0  # No valid bigrams = fragmented
        
        nll_per_char = total_nll / len(normalized)
        
        if self.debug_mode:
            logger.info(f"Bigram perplexity: {nll_per_char:.3f} nll/char")
        
        # Block if average negative log-likelihood > 3.2
        should_block = nll_per_char > 3.2
        return should_block, nll_per_char
    
    def check_producer_tagging(self, pdf_metadata: Dict, text_density: float, 
                             tokens_per_100_chars: float) -> bool:
        """
        Producer/tagging lock: Figma/Canva PDFs lack proper structure
        """
        producer = pdf_metadata.get('producer', '').lower()
        creator = pdf_metadata.get('creator', '').lower()
        has_struct_tree = pdf_metadata.get('has_struct_tree', False)
        has_mark_info = pdf_metadata.get('has_mark_info', False)
        
        if self.debug_mode:
            logger.info(f"Producer: {producer}, Creator: {creator}")
            logger.info(f"Has StructTree: {has_struct_tree}, Has MarkInfo: {has_mark_info}")
        
        # Check for Figma/Canva producers
        figma_canva_producers = {'figma', 'canva', 'skia', 'chrome pdf plugin'}
        is_figma_canva = any(p in producer or p in creator for p in figma_canva_producers)
        
        if not is_figma_canva:
            return False
        
        # Block if Figma/Canva AND (no structure OR low density OR high fragmentation)
        should_block = (
            not has_struct_tree or 
            text_density < 120 or 
            tokens_per_100_chars >= 1.6
        )
        
        if self.debug_mode and should_block:
            logger.info(f"Producer lock triggered: figma_canva={is_figma_canva}, "
                       f"no_struct={not has_struct_tree}, density={text_density}, "
                       f"fragmentation={tokens_per_100_chars}")
        
        return should_block
    
    def log_debug_info(self, text: str, triggers: List[str], **metrics):
        """Log debug information when PREFLIGHT_DEBUG=1"""
        if not self.debug_mode:
            return
        
        logger.info("=== DETERMINISTIC LOCK DEBUG ===")
        logger.info(f"Triggers: {triggers}")
        
        for key, value in metrics.items():
            logger.info(f"{key}: {value}")
        
        # Log first 300 chars with markers
        preview = text[:300]
        marked = preview.replace(' ', '·').replace('\u00A0', '⍽').replace('\n', '¶')
        logger.info(f"Text preview: {marked}")
        logger.info("=== END DEBUG ===")

# Global instance
deterministic_locks = DeterministicLocks()
