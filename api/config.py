"""
Configuration and feature flags for the enhanced keyword extraction system.
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class for feature flags and settings."""
    
    def __init__(self):
        # Feature flags from environment variables
        self.SEMANTIC_ON = os.getenv("SEMANTIC_ON", "0") == "1"
        self.PY_SIDECAR_ON = os.getenv("PY_SIDECAR_ON", "0") == "1"
        
        # Performance settings
        self.SEMANTIC_TIMEOUT_MS = int(os.getenv("SEMANTIC_TIMEOUT_MS", "1200"))
        self.SIDECAR_TIMEOUT_MS = int(os.getenv("SIDECAR_TIMEOUT_MS", "2000"))
        
        # Keyword extraction settings
        self.MAX_KEYWORDS = int(os.getenv("MAX_KEYWORDS", "30"))
        self.MAX_MISSING_KEYWORDS = int(os.getenv("MAX_MISSING_KEYWORDS", "7"))
        self.MAX_BULLET_SUGGESTIONS = int(os.getenv("MAX_BULLET_SUGGESTIONS", "10"))
        
        # Fuzzy matching settings
        self.FUZZY_MATCH_THRESHOLD = int(os.getenv("FUZZY_MATCH_THRESHOLD", "90"))
        
        # Cache settings
        self.ENABLE_CACHE = os.getenv("ENABLE_CACHE", "1") == "1"
        self.CACHE_DIR = os.getenv("CACHE_DIR", ".cache")
        
        # Debug settings
        self.DEBUG_MODE = os.getenv("DEBUG_MODE", "0") == "1"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "semantic_on": self.SEMANTIC_ON,
            "py_sidecar_on": self.PY_SIDECAR_ON,
            "semantic_timeout_ms": self.SEMANTIC_TIMEOUT_MS,
            "sidecar_timeout_ms": self.SIDECAR_TIMEOUT_MS,
            "max_keywords": self.MAX_KEYWORDS,
            "max_missing_keywords": self.MAX_MISSING_KEYWORDS,
            "max_bullet_suggestions": self.MAX_BULLET_SUGGESTIONS,
            "fuzzy_match_threshold": self.FUZZY_MATCH_THRESHOLD,
            "enable_cache": self.ENABLE_CACHE,
            "cache_dir": self.CACHE_DIR,
            "debug_mode": self.DEBUG_MODE,
            "log_level": self.LOG_LEVEL
        }
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags for API response."""
        return {
            "semantic_similarity": self.SEMANTIC_ON,
            "python_sidecar": self.PY_SIDECAR_ON,
            "enhanced_keywords": True,  # Always enabled
            "fuzzy_matching": True,     # Always enabled
            "bullet_suggestions": True  # Always enabled
        }

# Global configuration instance
config = Config()

