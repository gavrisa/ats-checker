from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import re
import logging
import os
import hashlib
from typing import List, Dict, Any, Set, Tuple
from collections import Counter
import random

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Binary integrity tracking
def compute_file_hash(file_content: bytes) -> str:
    """Compute SHA-256 hash of file content"""
    return hashlib.sha256(file_content).hexdigest()

def log_file_integrity(stage: str, file_content: bytes, filename: str = ""):
    """Log file integrity at different stages"""
    size = len(file_content)
    hash_short = compute_file_hash(file_content)[:8]
    logger.info(f"INTEGRITY [{stage}] {filename}: size={size}, hash={hash_short}")

# Debug mode for whitespace visibility
def show_whitespace_visible(text: str) -> str:
    """Make whitespace characters visible for debugging"""
    return (text.replace(' ', '·')
                .replace('\u00A0', '⍽')   # NBSP
                .replace('\u2009', ' ')   # thin space
                .replace('\u200A', ' ')   # hair space
                .replace('\u200B', '⎵')   # zero-width space
                .replace('\n', '¶'))

def log_whitespace_debug(text: str, stage: str):
    """Log whitespace debugging information"""
    if os.getenv('PREFLIGHT_DEBUG', '0') == '1':
        visible_text = show_whitespace_visible(text[:300])
        tokens = text.split()
        token_info = [f"{t}|{len(t)}" for t in tokens[:20]]
        logger.info(f"WHITESPACE_DEBUG [{stage}]: {visible_text}")
        logger.info(f"TOKENS_DEBUG [{stage}]: {token_info}")

# Import the smart keyword extractor
try:
    from simple_smart_extractor import SimpleSmartExtractor
    SMART_EXTRACTOR_AVAILABLE = True
    SmartKeywordExtractor = SimpleSmartExtractor  # Use simple version
    logger.info("✅ SUCCESS: Using simple smart keyword extractor (no external dependencies)")
    logger.info("✅ SimpleSmartExtractor imported successfully")
except ImportError as e:
    logger.error(f"❌ FAILED: Simple smart keyword extractor not available: {e}")
    try:
        from smart_keyword_extractor import SmartKeywordExtractor
        SMART_EXTRACTOR_AVAILABLE = True
        logger.info("✅ SUCCESS: Using full smart keyword extractor with NLP dependencies")
    except ImportError as e2:
        logger.error(f"❌ FAILED: Full smart keyword extractor also not available: {e2}")
        SMART_EXTRACTOR_AVAILABLE = False

# Import the deterministic preflight system
try:
    logger.info("Attempting to import deterministic preflight system...")
    from deterministic_preflight import preflight_document, compute_file_integrity, extract_text_with_preflight
    PREFLIGHT_AVAILABLE = True
    logger.info("✅ SUCCESS: Deterministic preflight system imported successfully")
except ImportError as e:
    logger.error(f"❌ FAILED: Deterministic preflight system not available: {e}")
    PREFLIGHT_AVAILABLE = False
except Exception as e:
    logger.error(f"❌ FAILED: Unexpected error importing deterministic preflight system: {e}")
    PREFLIGHT_AVAILABLE = False

app = FastAPI(title="ATS Resume Checker", version="2.1.2")

# Initialize smart keyword extractor
smart_extractor = None
if SMART_EXTRACTOR_AVAILABLE:
    try:
        smart_extractor = SmartKeywordExtractor(data_dir="data")
        logger.info("Smart keyword extractor initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize smart keyword extractor: {e}")
        smart_extractor = None

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Blacklist - Always exclude these words/phrases
BLACKLIST = {
    # Pronouns & auxiliary verbs
    'i', 'you', 'we', 'they', 'he', 'she', 'it', 'your', 'our', 'their', 'my', 'his', 'her', 'its',
    'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall',
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    
    # Generic phrases
    'you will', 'you are', 'designs are', 'part of', 'our team',
    
    # Filler / vague terms
    'good', 'great', 'strong', 'excellent', 'best', 'better', 'successful', 'proven', 'passionate',
    'experience', 'experiences', 'skills', 'background', 'knowledge', 'expertise',
    'work', 'working', 'workers', 'teamwork', 'team', 'people', 'company', 'business', 'project', 'role',
    
    # Common verbs (too broad)
    'make', 'create', 'support', 'help', 'give', 'take', 'show', 'use', 'ensure', 'provide', 'manage',
    
    # Unwanted job titles (too generic)
    'designer', 'designs', 'product managers', 'manager', 'leaders', 'leadership', 'stakeholder',
    
    # Additional generic terms to exclude
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
    'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there',
    'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
    'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
    'too', 'very', 'just', 'now', 'really', 'quite', 'rather', 'almost', 'nearly',
    'looking', 'seeking', 'hiring', 'recruiting', 'searching', 'finding', 'identifying',
    'selecting', 'choosing', 'picking', 'deciding', 'determining', 'establishing',
    'setting', 'defining', 'describing', 'explaining', 'clarifying', 'specifying',
    'detailing', 'outlining', 'summarizing', 'reviewing', 'evaluating', 'assessing',
    'analyzing', 'examining', 'investigating', 'studying', 'researching', 'exploring',
    'discovering', 'learning', 'understanding', 'knowing', 'recognizing', 'realizing',
    'seeing', 'noticing', 'observing', 'watching', 'monitoring', 'tracking', 'following',
    'pursuing', 'chasing', 'using', 'utilizing', 'applying', 'employing', 'leveraging',
    'taking', 'doing', 'getting', 'having', 'being', 'becoming', 'turning', 'going',
    'coming', 'moving', 'changing', 'improving', 'enhancing', 'optimizing', 'streamlining'
}

# Phrase-level blacklist (n-grams) - exact phrases to exclude
PHRASE_BLACKLIST = {
    # Day one variations
    'day one', 'day-one', 'from day one', 'on day one', 'starting day one',
    
    # Generic phrases
    'you will', 'you are', 'designs are', 'part of', 'our team',
    
    # Verb + object fragments (incomplete clauses)
    'conduct user', 'combine', 'collaborate', 'implement', 'develop', 'create', 'build',
    'manage', 'lead', 'guide', 'assist', 'support', 'help', 'provide', 'ensure',
    
    # Generic job titles
    'product manager', 'product managers', 'senior designer', 'lead designer',
    'ux designer', 'ui designer', 'designer', 'manager', 'leader',
    
    # Fragment & filler phrases
    'products that', 'looking portfolios', 'fully remote', 'please', 'join', 'look', 'client',
    'senior', 'designer', 'content', 'platform',  # Alone (generic)
    
    # HR / employment / location / recruiting
    'fully', 'remote', 'europe', 'eu', 'relocation', 'visa', 'apply', 'benefits', 'compensation',
    
    # Generic nouns & bare stems (unless part of an allowed bigram)
    'client', 'clients', 'user', 'users', 'mobile', 'platform', 'content', 'app', 'apps', 
    'product', 'portfolio', 'senior', 'designer',
    
    # Fragments & filler
    'look', 'that', 'end design', 'what', 'ideally', 'corporate', 'craft', 'plu',
    'includ', 'please', 'portfolio', 'consumer', 'remote', 'europe', 'join', 'info', 'client',
    'design processs', 'innovative multi', 'systems translate', 'monetization looking', 'design chat',
    
    # Generic/miscellaneous words (not skills/tools/methods) - SPECIFIC TARGETS
    'real', 'help', 'meaningful', 'part', 'inform', 'decision', 'solution', 'impact', 'explore', 'journey',
    'deel', 'statu', 'companie', 'every', 'tool', 'world', 'employer', 'status', 'reflect', 'fast',
    'every', 'part', 'tool', 'world', 'company', 'employer', 'status', 'reflect', 'fast', 'every',
    
    # Malformed/broken words that should be excluded
    'statu', 'companie', 'proces', 'experienc', 'countrie', 'covey', 'deel', 'rewards', 'employer',
    'accommodation', 'talent', 'career', 'connect', 'review', 'reward', 'global', 'customer',
    'employment', 'equal', 'payroll', 'countries', 'companies', 'experience', 'process', 'rewards',
    'prototyp', 'requir', 'desig', 'test', 'work', 'play', 'creat', 'build', 'mak', 'us', 'learn',
    'team', 'teams', 'believe', 'think', 'feel', 'know', 'understand', 'learn', 'remember', 'forget',
    'notice', 'realize', 'recognize', 'appreciate', 'value', 'prefer', 'choose', 'decide', 'plan',
    'organize', 'arrange', 'prepare', 'develop', 'grow', 'improve', 'change', 'transform', 'adapt',
    'adjust', 'modify', 'update', 'upgrade', 'enhance', 'optimize', 'maximize', 'minimize', 'reduce',
    'increase', 'decrease', 'expand', 'contract', 'extend', 'limit', 'restrict', 'control', 'manage',
    'handle', 'deal', 'cope', 'address', 'tackle', 'approach', 'method', 'way', 'manner', 'style',
    'strategy', 'tactic', 'technique', 'process', 'procedure', 'step', 'stage', 'phase', 'level',
    'degree', 'extent', 'scope', 'range', 'area', 'field', 'domain', 'sector', 'industry', 'market',
    'business', 'company', 'organization', 'institution', 'entity', 'group', 'unit', 'department',
    'division', 'section', 'branch', 'office', 'location', 'place', 'site', 'venue', 'space',
    'environment', 'setting', 'context', 'situation', 'condition', 'state', 'status', 'position',
    'role', 'function', 'purpose', 'goal', 'objective', 'target', 'aim', 'intention', 'plan',
    'strategy', 'approach', 'method', 'technique', 'tool', 'resource', 'asset', 'capital',
    'investment', 'cost', 'price', 'value', 'worth', 'benefit', 'advantage', 'disadvantage',
    'challenge', 'problem', 'issue', 'concern', 'risk', 'threat', 'opportunity', 'potential',
    'possibility', 'chance', 'probability', 'likelihood', 'certainty', 'uncertainty', 'confidence',
    'trust', 'belief', 'faith', 'hope', 'expectation', 'assumption', 'hypothesis', 'theory',
    'concept', 'idea', 'notion', 'thought', 'opinion', 'view', 'perspective', 'angle', 'aspect',
    'facet', 'dimension', 'element', 'component', 'piece', 'section', 'segment', 'portion',
    'fraction', 'percentage', 'ratio', 'proportion', 'rate', 'speed', 'pace', 'tempo', 'rhythm',
    'pattern', 'trend', 'tendency', 'direction', 'course', 'path', 'route', 'way', 'means',
    'method', 'approach', 'technique', 'strategy', 'tactic', 'plan', 'scheme', 'design',
    'structure', 'framework', 'system', 'model', 'template', 'format', 'layout', 'arrangement',
    'organization', 'configuration', 'setup', 'installation', 'implementation', 'execution',
    'delivery', 'completion', 'finish', 'end', 'result', 'outcome', 'consequence', 'effect',
    'influence', 'contribution', 'input', 'output', 'product', 'deliverable', 'artifact',
    'creation', 'production', 'generation', 'development', 'construction', 'building', 'making',
    'creating', 'designing', 'planning', 'organizing', 'managing', 'leading', 'guiding',
    'directing', 'supervising', 'overseeing', 'monitoring', 'tracking', 'measuring', 'evaluating',
    'assessing', 'analyzing', 'reviewing', 'examining', 'studying', 'researching', 'investigating',
    'exploring', 'discovering', 'finding', 'identifying', 'recognizing', 'detecting', 'noticing',
    'observing', 'watching', 'seeing', 'looking', 'viewing', 'reading', 'listening', 'hearing',
    'feeling', 'touching', 'tasting', 'smelling', 'experiencing', 'encountering', 'meeting',
    'facing', 'confronting', 'challenging', 'questioning', 'asking', 'inquiring', 'requesting',
    'demanding', 'requiring', 'needing', 'wanting', 'desiring', 'wishing', 'hoping', 'expecting',
    'anticipating', 'predicting', 'forecasting', 'projecting', 'estimating', 'calculating',
    'computing', 'processing', 'handling', 'managing', 'controlling', 'regulating', 'governing',
    'ruling', 'leading', 'guiding', 'directing', 'instructing', 'teaching', 'training',
    'educating', 'coaching', 'mentoring', 'advising', 'consulting', 'counseling', 'supporting',
    'helping', 'assisting', 'aiding', 'facilitating', 'enabling', 'empowering', 'encouraging',
    'motivating', 'inspiring', 'influencing', 'persuading', 'convincing', 'encouraging',
    'promoting', 'advocating', 'recommending', 'suggesting', 'proposing', 'offering', 'providing',
    'supplying', 'delivering', 'distributing', 'sharing', 'communicating', 'transmitting',
    'conveying', 'expressing', 'articulating', 'explaining', 'describing', 'defining', 'clarifying',
    'specifying', 'detailing', 'outlining', 'summarizing', 'reporting', 'documenting', 'recording',
    'logging', 'tracking', 'monitoring', 'observing', 'watching', 'supervising', 'overseeing',
    'managing', 'controlling', 'regulating', 'governing',
    
    # Additional generic words (duplicates removed)
    'understand', 'learn', 'know', 'think', 'feel', 'believe', 'consider', 'imagine', 'remember',
    'forget', 'notice', 'realize', 'recognize', 'appreciate', 'value', 'prefer', 'choose', 'decide',
    'plan', 'organize', 'arrange', 'prepare', 'develop', 'grow', 'improve', 'change', 'transform',
    'adapt', 'adjust', 'modify', 'update', 'upgrade', 'enhance', 'optimize', 'maximize', 'minimize',
    'reduce', 'increase', 'decrease', 'expand', 'contract', 'extend', 'limit', 'restrict', 'control',
    'manage', 'handle', 'deal', 'cope', 'handle', 'address', 'tackle', 'approach', 'method', 'way',
    'manner', 'style', 'approach', 'strategy', 'tactic', 'technique', 'process', 'procedure', 'step',
    'stage', 'phase', 'level', 'degree', 'extent', 'scope', 'range', 'area', 'field', 'domain',
    'sector', 'industry', 'market', 'business', 'company', 'organization', 'institution', 'entity',
    'group', 'team', 'unit', 'department', 'division', 'section', 'branch', 'office', 'location',
    'place', 'site', 'venue', 'space', 'environment', 'setting', 'context', 'situation', 'condition',
    'state', 'status', 'position', 'role', 'function', 'purpose', 'goal', 'objective', 'target',
    'aim', 'intention', 'plan', 'strategy', 'approach', 'method', 'technique', 'tool', 'resource',
    'asset', 'capital', 'investment', 'cost', 'price', 'value', 'worth', 'benefit', 'advantage',
    'disadvantage', 'challenge', 'problem', 'issue', 'concern', 'risk', 'threat', 'opportunity',
    'potential', 'possibility', 'chance', 'probability', 'likelihood', 'certainty', 'uncertainty',
    'confidence', 'trust', 'belief', 'faith', 'hope', 'expectation', 'assumption', 'hypothesis',
    'theory', 'concept', 'idea', 'notion', 'thought', 'opinion', 'view', 'perspective', 'angle',
    'aspect', 'facet', 'dimension', 'element', 'component', 'part', 'piece', 'section', 'segment',
    'portion', 'fraction', 'percentage', 'ratio', 'proportion', 'rate', 'speed', 'pace', 'tempo',
    'rhythm', 'pattern', 'trend', 'tendency', 'direction', 'course', 'path', 'route', 'way',
    'means', 'method', 'approach', 'technique', 'strategy', 'tactic', 'plan', 'scheme', 'design',
    'structure', 'framework', 'system', 'model', 'template', 'format', 'layout', 'arrangement',
    'organization', 'configuration', 'setup', 'installation', 'implementation', 'execution',
    'delivery', 'completion', 'finish', 'end', 'result', 'outcome', 'consequence', 'effect',
    'impact', 'influence', 'contribution', 'input', 'output', 'product', 'deliverable', 'artifact',
    'creation', 'production', 'generation', 'development', 'construction', 'building', 'making',
    'creating', 'designing', 'planning', 'organizing', 'managing', 'leading', 'guiding', 'directing',
    'supervising', 'overseeing', 'monitoring', 'tracking', 'measuring', 'evaluating', 'assessing',
    'analyzing', 'reviewing', 'examining', 'studying', 'researching', 'investigating', 'exploring',
    'discovering', 'finding', 'identifying', 'recognizing', 'detecting', 'noticing', 'observing',
    'watching', 'seeing', 'looking', 'viewing', 'reading', 'listening', 'hearing', 'feeling',
    'touching', 'tasting', 'smelling', 'experiencing', 'encountering', 'meeting', 'facing',
    'confronting', 'challenging', 'questioning', 'asking', 'inquiring', 'requesting', 'demanding',
    'requiring', 'needing', 'wanting', 'desiring', 'wishing', 'hoping', 'expecting', 'anticipating',
    'predicting', 'forecasting', 'projecting', 'estimating', 'calculating', 'computing', 'processing',
    'handling', 'managing', 'controlling', 'regulating', 'governing', 'ruling', 'leading', 'guiding',
    'directing', 'instructing', 'teaching', 'training', 'educating', 'coaching', 'mentoring',
    'advising', 'consulting', 'counseling', 'supporting', 'helping', 'assisting', 'aiding',
    'facilitating', 'enabling', 'empowering', 'encouraging', 'motivating', 'inspiring', 'influencing',
    'persuading', 'convincing', 'encouraging', 'promoting', 'advocating', 'recommending', 'suggesting',
    'proposing', 'offering', 'providing', 'supplying', 'delivering', 'distributing', 'sharing',
    'communicating', 'transmitting', 'conveying', 'expressing', 'articulating', 'explaining',
    'describing', 'defining', 'clarifying', 'specifying', 'detailing', 'outlining', 'summarizing',
    'reporting', 'documenting', 'recording', 'logging', 'tracking', 'monitoring', 'observing',
    'watching', 'supervising', 'overseeing', 'managing', 'controlling', 'regulating', 'governing',
    
    # Role/level titles
    'senior product', 'product designer', 'senior product designer', 'product manager',
    
    # Sensitive/domain words
    'adult', 'adult content', 'nsfw', 'consumer apps',
    
    # Company/Brand names (exclude from keywords)
    'autronica', 'onlyfans', 'behance', 'restream', 'google', 'microsoft', 'apple', 'amazon',
    'facebook', 'meta', 'twitter', 'linkedin', 'instagram', 'tiktok', 'youtube', 'netflix',
    'spotify', 'uber', 'airbnb', 'tesla', 'spacex', 'openai', 'anthropic', 'stripe',
    'paypal', 'shopify', 'salesforce', 'adobe', 'oracle', 'ibm', 'intel', 'nvidia',
    'samsung', 'sony', 'nintendo', 'disney', 'warner', 'universal', 'paramount'
}

# Leading/trailing stopwords to trim from phrases
TRIM_STOPWORDS = {
    'that', 'of', 'for', 'to', 'with', 'in', 'at', 'by', 'on', 'from', 'the', 'a', 'an',
    'and', 'or', 'but', 'is', 'are', 'was', 'were', 'be', 'been', 'being'
}

# Minimum signal rule - words that are too weak to keep alone
MINIMUM_SIGNAL_WORDS = {
    # Auxiliaries, pronouns, determiners
    'i', 'you', 'we', 'they', 'he', 'she', 'it', 'your', 'our', 'their', 'my', 'his', 'her', 'its',
    'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall',
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
    'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there',
    'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
    'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
    'too', 'very', 'just', 'now', 'really', 'quite', 'rather', 'almost', 'nearly',
    
    # Generic verbs without domain context
    'make', 'create', 'support', 'help', 'give', 'take', 'show', 'use', 'ensure', 'provide', 'manage',
    'combine', 'collaborate', 'implement', 'develop', 'build', 'lead', 'guide', 'assist', 'support',
    
    # Generic descriptive words
    'good', 'great', 'strong', 'excellent', 'best', 'better', 'successful', 'proven', 'passionate',
    'experience', 'experiences', 'skills', 'background', 'knowledge', 'expertise',
    'work', 'working', 'workers', 'teamwork', 'team', 'people', 'company', 'business', 'project', 'role'
}

# Whitelist - Always keep these words/phrases (allowed categories only)
WHITELIST = {
    # Methods & practices
    'prototyping', 'usability testing', 'user research', 'accessibility', 'interaction design', 
    'discovery', 'ideation', 'end-to-end design', 'design systems',
    
    # Tools/tech
    'figma', 'sketch', 'miro', 'jira', 'confluence', 'analytics',
    
    # Deliverables/artefacts
    'wireframes', 'flows', 'journey maps', 'personas', 'design tokens',
    
    # Process/frameworks
    'agile', 'scrum', 'a/b testing', 'design ops',
    
    # Outcome/metrics (when paired)
    'conversion optimization', 'kpi', 'experimentation',
    
    # AI & Technology specific terms
    'ai companionship', 'conversational ai', 'gamification', 'premium monetization',
    'chat interfaces', 'creation tools', 'payment flows', 'translate complex',
    'intuitive engaging', 'shipping impactful', 'consumer-facing apps', 'adult content apps',
    'html/css', 'motion design', '3d design',
    
    # Additional design/process/tool/skill terms - PRIORITY JOB-RELEVANT TERMS
    'procurement teams', 'supplier', 'collaboration', 'developer', 'developers', 'engineering',
    'cross-functional', 'stakeholders', 'workflows', 'validation', 'testing', 'research',
    'analysis', 'synthesis', 'iteration', 'feedback', 'insights', 'metrics', 'data',
    'performance', 'optimization', 'efficiency', 'usability', 'functionality', 'reliability',
    'scalability', 'maintainability', 'compatibility', 'integration', 'deployment', 'delivery',
    'automation', 'standardization', 'documentation', 'specification', 'requirements',
    'architecture', 'infrastructure', 'platform', 'framework', 'library', 'component',
    'module', 'service', 'api', 'database', 'backend', 'frontend', 'full-stack',
    'responsive', 'adaptive', 'progressive', 'incremental', 'iterative', 'agile',
    'lean', 'kanban', 'sprint', 'retrospective', 'standup', 'planning', 'estimation',
    'prioritization', 'roadmap', 'milestone', 'deadline', 'timeline', 'schedule',
    'budget', 'resource', 'capacity', 'velocity', 'throughput', 'quality', 'testing',
    'qa', 'debugging', 'troubleshooting', 'monitoring', 'logging', 'alerting',
    'security', 'privacy', 'compliance', 'governance', 'audit', 'review', 'approval',
    
    # SPECIFIC JOB-RELEVANT TERMS (always keep these)
    'ignite', 'system improvements', 'complex workflows', 'user journey', 'decision-making'
}

# Tool/Skill brands that should be kept (even though they're brand names)
TOOL_SKILL_BRANDS = {
    'figma', 'sketch', 'adobe', 'photoshop', 'illustrator', 'indesign', 'after effects',
    'premiere', 'miro', 'jira', 'confluence', 'slack', 'notion', 'zeplin', 'invision',
    'principle', 'framer', 'webflow', 'wordpress', 'shopify', 'squarespace', 'wix',
    'github', 'gitlab', 'bitbucket', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
    'react', 'vue', 'angular', 'node', 'python', 'javascript', 'typescript', 'html',
    'css', 'sass', 'less', 'bootstrap', 'tailwind', 'material', 'antd', 'chakra'
}

# Allowed bigrams/trigrams (keep these even if individual words are blacklisted)
ALLOWED_PHRASES = {
    # Mobile app design variations
    'mobile app design', 'mobile app', 'mobile design',
    
    # Product design variations
    'product design', 'product strategy', 'product lifecycle',
    
    # Content design variations
    'content design', 'content strategy',
    
    # Cross-functional collaboration
    'cross-functional collaboration', 'cross-functional teams',
    
    # User experience variations
    'user experience', 'user interface', 'user journey',
    
    # Design system variations
    'design system', 'design tokens', 'design ops',
    
    # End-to-end variations
    'end-to-end design', 'end-to-end ownership', 'end-to-end',
    
    # AI & Technology specific phrases
    'ai companionship', 'conversational ai', 'premium monetization', 'chat interfaces',
    'creation tools', 'payment flows', 'translate complex', 'intuitive engaging',
    'prototyping ideas', 'shipping impactful', 'consumer-facing apps', 'adult content apps',
    'motion design', '3d design',
    
    # Whitelisted compound phrases (keep these even if individual words are blacklisted)
    'user journey', 'decision-making', 'system improvements', 'complex workflows', 'procurement teams'
}

def normalize_text(text: str) -> str:
    """Normalize text for processing"""
    # Remove special characters, keep only alphanumeric and spaces
    text = re.sub(r'[^\w\s-]', ' ', text.lower())
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def normalize_word(word: str) -> str:
    """Normalize word forms (e.g., executed/executing → execution)"""
    # Only normalize common verb forms to their base form
    verb_endings = [
        ('ing', ''),      # executing → execut
        ('ed', ''),       # executed → execut
        ('s', ''),        # executes → execut
        ('es', ''),       # processes → process
        ('ies', 'y'),     # studies → study
        ('ied', 'y'),     # studied → study
    ]
    
    # Apply only basic verb normalizations
    normalized = word
    for ending, replacement in verb_endings:
        if word.endswith(ending) and len(word) > len(ending) + 2:
            # Check if the resulting word is still meaningful
            candidate = word[:-len(ending)] + replacement
            if len(candidate) >= 3:
                normalized = candidate
                break
    
    # Don't remove prefixes or other endings to preserve meaningful words
    return normalized

def normalize_phrases(text: str) -> str:
    """Normalize specific phrases and fix noisy JD tokens"""
    # Map specific noisy tokens to correct forms
    phrase_mappings = {
        'user-center': 'user-centered',
        'usability test': 'usability testing',
        'conduct user': '',  # Drop verb + object fragment
        'product manager': '',  # Drop generic title
        'product managers': '',  # Drop generic title
        'senior designer': '',  # Drop generic title
        'lead designer': '',  # Drop generic title
        'ux designer': '',  # Drop generic title
        'ui designer': '',  # Drop generic title
        'usability testinging': 'usability testing',  # Fix double normalization
        'processe': 'process',  # Fix normalization
        'methodologie': 'methodology',  # Fix normalization
        'end product design': 'product design',  # Pick domain term
        'end product': 'product design',  # Pick domain term
        'product design design': 'product design',  # Remove duplicate word
        'design design': 'design',  # Remove duplicate word
        'senior senior': 'senior',  # Remove duplicate word
        'product product': 'product',  # Remove duplicate word
        'end-to-end design': 'end-to-end design',  # Keep as is
    }
    
    normalized_text = text
    for old_phrase, new_phrase in phrase_mappings.items():
        if old_phrase in normalized_text:
            if new_phrase:  # Replace with correct form
                normalized_text = normalized_text.replace(old_phrase, new_phrase)
            else:  # Remove completely
                normalized_text = normalized_text.replace(old_phrase, '')
    
    # Remove phrases that start or end with hyphens/dashes
    normalized_text = re.sub(r'\s*-\s*\w+', '', normalized_text)  # Remove "- word"
    normalized_text = re.sub(r'\w+\s*-\s*', '', normalized_text)  # Remove "word -"
    
    # Clean up extra spaces
    normalized_text = re.sub(r'\s+', ' ', normalized_text.strip())
    return normalized_text

def is_company_brand_name(word: str) -> bool:
    """Check if a word is likely a company/brand name that should be excluded"""
    # Convert to lowercase for comparison
    word_lower = word.lower()
    
    # Check if it's in the company blacklist
    if word_lower in PHRASE_BLACKLIST:
        return True
    
    # Check if it's a tool/skill brand (keep these)
    if word_lower in TOOL_SKILL_BRANDS:
        return False
    
    # Check if it's a proper noun (starts with capital letter and is not a common word)
    if (word[0].isupper() and 
        len(word) >= 3 and 
        word_lower not in WHITELIST and 
        word_lower not in ALLOWED_PHRASES and
        word_lower not in MINIMUM_SIGNAL_WORDS):
        
        # Additional heuristics for company names
        # Skip if it contains numbers (like "iPhone 14")
        if any(char.isdigit() for char in word):
            return True
        
        # Skip if it's a common word that happens to be capitalized
        common_capitalized = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'out', 'off', 'over', 'under', 'again', 'further',
            'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how'
        }
        
        if word_lower in common_capitalized:
            return False
        
        # Likely a company/brand name
        return True
    
    return False

def is_skill_tool_method(word: str) -> bool:
    """Check if a word represents a skill, tool, method, or domain-specific term"""
    word_lower = word.lower()
    
    # Check if it's in whitelist (always keep)
    if word_lower in WHITELIST:
        return True
    
    # Check if it's a tool/skill brand (always keep)
    if word_lower in TOOL_SKILL_BRANDS:
        return True
    
    # Check if it's in allowed phrases (always keep)
    if word_lower in ALLOWED_PHRASES:
        return True
    
    # Check if it's a technical term (contains common tech patterns)
    tech_patterns = [
        'api', 'ui', 'ux', 'css', 'html', 'js', 'jsx', 'ts', 'tsx', 'sql', 'json', 'xml',
        'http', 'https', 'rest', 'graphql', 'oauth', 'jwt', 'aws', 'gcp', 'azure',
        'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab', 'bitbucket',
        'npm', 'yarn', 'webpack', 'babel', 'eslint', 'prettier', 'jest', 'cypress',
        'react', 'vue', 'angular', 'node', 'express', 'django', 'flask', 'rails',
        'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'kafka',
        'figma', 'sketch', 'adobe', 'photoshop', 'illustrator', 'indesign',
        'miro', 'jira', 'confluence', 'slack', 'notion', 'zeplin', 'invision'
    ]
    
    if any(pattern in word_lower for pattern in tech_patterns):
        return True
    
    # Check if it's a design/development method (PRIORITY JOB-RELEVANT TERMS)
    method_patterns = [
        'design', 'prototype', 'wireframe', 'mockup', 'userflow', 'persona', 'journey',
        'research', 'testing', 'validation', 'iteration', 'agile', 'scrum', 'kanban',
        'sprint', 'retrospective', 'standup', 'planning', 'estimation', 'roadmap',
        'milestone', 'deadline', 'timeline', 'budget', 'resource', 'capacity',
        'velocity', 'throughput', 'quality', 'qa', 'debugging', 'troubleshooting',
        'monitoring', 'logging', 'alerting', 'security', 'privacy', 'compliance',
        'governance', 'audit', 'review', 'approval', 'deployment', 'delivery',
        'automation', 'standardization', 'documentation', 'specification',
        'requirements', 'architecture', 'infrastructure', 'platform', 'framework',
        'library', 'component', 'module', 'service', 'database', 'backend',
        'frontend', 'full-stack', 'responsive', 'adaptive', 'progressive',
        'incremental', 'iterative', 'lean', 'performance', 'optimization',
        'efficiency', 'usability', 'functionality', 'reliability', 'scalability',
        'maintainability', 'compatibility', 'integration', 'analysis', 'synthesis',
        'feedback', 'insights', 'metrics', 'data', 'collaboration', 'stakeholders',
        'workflows', 'cross-functional', 'developer', 'developers', 'engineering',
        'procurement', 'supplier', 'teams', 'ignite', 'improvements', 'complex'
    ]
    
    if any(pattern in word_lower for pattern in method_patterns):
        return True
    
    # Check for specific job-relevant terms that should always be kept
    priority_terms = [
        'discovery', 'accessibility', 'usability', 'interaction', 'flows', 'personas',
        'wireframes', 'systems', 'prototyping', 'collaboration', 'stakeholders',
        'cross-functional', 'workflows', 'validation', 'testing', 'research',
        'analysis', 'synthesis', 'iteration', 'feedback', 'insights', 'metrics',
        'performance', 'optimization', 'efficiency', 'usability', 'functionality',
        'reliability', 'scalability', 'maintainability', 'compatibility', 'integration',
        'deployment', 'delivery', 'automation', 'standardization', 'documentation',
        'specification', 'requirements', 'architecture', 'infrastructure', 'platform',
        'framework', 'library', 'component', 'module', 'service', 'database',
        'backend', 'frontend', 'full-stack', 'responsive', 'adaptive', 'progressive',
        'incremental', 'iterative', 'lean', 'developer', 'developers', 'engineering',
        'procurement', 'supplier', 'teams', 'ignite', 'improvements', 'complex'
    ]
    
    if word_lower in priority_terms:
        return True
    
    # If none of the above, it's likely a filler word
    return False

def canonicalize_phrase(phrase: str) -> str:
    """Canonicalize a phrase: lowercase, trim, collapse spaces/hyphens, lemmatize"""
    # Lowercase and trim
    canonical = phrase.lower().strip()
    
    # Collapse spaces and hyphens
    canonical = re.sub(r'[-\s]+', ' ', canonical)
    
    # Trim leading/trailing stopwords
    words = canonical.split()
    while words and words[0] in TRIM_STOPWORDS:
        words.pop(0)
    while words and words[-1] in TRIM_STOPWORDS:
        words.pop()
    
    # Remove consecutive duplicate words (e.g., "product design design" -> "product design")
    cleaned_words = []
    for word in words:
        if not cleaned_words or word != cleaned_words[-1]:
            cleaned_words.append(word)
    
    # Rejoin and clean up
    canonical = ' '.join(cleaned_words).strip()
    
    # Drop if empty or only stopwords after trimming
    if not canonical or all(word in TRIM_STOPWORDS for word in canonical.split()):
        return ''
    
    return canonical

def compute_similarity(phrase1: str, phrase2: str) -> float:
    """Compute normalized similarity between two phrases using Jaccard on lemma tokens"""
    # Get lemma tokens for each phrase
    tokens1 = set(normalize_word(word) for word in phrase1.split())
    tokens2 = set(normalize_word(word) for word in phrase2.split())
    
    # Remove stopwords from tokens
    tokens1 = tokens1 - TRIM_STOPWORDS
    tokens2 = tokens2 - TRIM_STOPWORDS
    
    # Skip if either phrase has no meaningful tokens
    if not tokens1 or not tokens2:
        return 0.0
    
    # Compute Jaccard similarity
    intersection = len(tokens1.intersection(tokens2))
    union = len(tokens1.union(tokens2))
    
    if union == 0:
        return 0.0
    
    return intersection / union

def is_substring_phrase(phrase1: str, phrase2: str) -> bool:
    """Check if phrase1 is a strict substring token-wise of phrase2"""
    words1 = phrase1.split()
    words2 = phrase2.split()
    
    if len(words1) >= len(words2):
        return False
    
    # Check if words1 appears as a consecutive subsequence in words2
    for i in range(len(words2) - len(words1) + 1):
        if words2[i:i+len(words1)] == words1:
            return True
    
    return False

def deduplicate_keywords(candidates: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
    """Remove near-duplicate keywords using similarity and substring rules"""
    if not candidates:
        return []
    
    # Sort by score (descending) to prioritize higher-scoring candidates
    candidates = sorted(candidates, key=lambda x: x[1], reverse=True)
    
    # Canonicalize all candidates
    canonicalized = []
    for phrase, score in candidates:
        canonical = canonicalize_phrase(phrase)
        if canonical and len(canonical.split()) >= 1:  # At least one word
            canonicalized.append((canonical, score, phrase))  # Keep original for output
    
    # Remove exact duplicates (keep first occurrence)
    seen_canonical = set()
    unique_candidates = []
    for canonical, score, original in canonicalized:
        if canonical not in seen_canonical:
            seen_canonical.add(canonical)
            unique_candidates.append((original, score))
    
    # Apply near-duplicate collapse rules
    final_candidates = []
    for i, (phrase, score) in enumerate(unique_candidates):
        keep_this = True
        
        # Check against already accepted candidates
        for accepted_phrase, accepted_score in final_candidates:
            # Rule 1: If similarity >= 0.75, keep higher-scoring
            similarity = compute_similarity(phrase, accepted_phrase)
            if similarity >= 0.75:
                if score <= accepted_score:
                    keep_this = False
                    break
                else:
                    # Remove the lower-scoring accepted phrase
                    final_candidates = [(p, s) for p, s in final_candidates if p != accepted_phrase]
                break
        
            # Rule 2: If X is substring of X Y and both valid, keep X Y
            if is_substring_phrase(phrase, accepted_phrase):
                # Keep the longer phrase unless the shorter is whitelisted
                if phrase in WHITELIST and accepted_phrase not in WHITELIST:
                    # Remove the longer phrase, keep the whitelisted shorter one
                    final_candidates = [(p, s) for p, s in final_candidates if p != accepted_phrase]
                    break
        else:
                    keep_this = False
                    break
        
        if keep_this:
            final_candidates.append((phrase, score))
    
    return final_candidates

def extract_domain_tags(text: str) -> List[str]:
    """Extract domain-specific tags that should be shown separately"""
    domain_tags = []
    
    # Sensitive/domain words
    sensitive_domains = ['adult content', 'nsfw', 'consumer apps']
    for domain in sensitive_domains:
        if domain.lower() in text.lower():
            domain_tags.append(domain)
    
    # Location/employment tags
    location_tags = ['fully remote', 'europe', 'eu', 'relocation', 'visa']
    for tag in location_tags:
        if tag.lower() in text.lower():
            domain_tags.append(tag)
    
    return domain_tags

def extract_role_tags(text: str) -> List[str]:
    """Extract role/level titles that should be shown separately"""
    role_tags = []
    
    # Role/level titles
    role_patterns = [
        'senior product designer', 'product designer', 'senior designer', 
        'lead designer', 'ux designer', 'ui designer', 'product manager',
        'senior product', 'lead product', 'principal designer'
    ]
    
    for role in role_patterns:
        if role.lower() in text.lower():
            role_tags.append(role)
            break  # Only add the most specific role found
    
    return role_tags

def deduplicate_keywords_advanced(candidates: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
    """Advanced deduplication with better near-duplicate handling"""
    if not candidates:
        return []
    
    # Sort by score (descending) to prioritize higher-scoring candidates
    candidates = sorted(candidates, key=lambda x: x[1], reverse=True)
    
    # Canonicalize all candidates
    canonicalized = []
    for phrase, score in candidates:
        canonical = canonicalize_phrase(phrase)
        if canonical and len(canonical.split()) >= 1:  # At least one word
            canonicalized.append((canonical, score, phrase))  # Keep original for output
    
    # Remove exact duplicates (keep first occurrence)
    seen_canonical = set()
    unique_candidates = []
    for canonical, score, original in canonicalized:
        if canonical not in seen_canonical:
            seen_canonical.add(canonical)
            unique_candidates.append((original, score))
    
    # Apply advanced near-duplicate collapse rules
    final_candidates = []
    for phrase, score in unique_candidates:
        keep_this = True
        
        # Check against already accepted candidates
        for accepted_phrase, accepted_score in final_candidates:
            # Rule 1: If similarity >= 0.75, keep higher-scoring
            similarity = compute_similarity(phrase, accepted_phrase)
            if similarity >= 0.75:
                if score <= accepted_score:
                    keep_this = False
                    break
                else:
                    # Remove the lower-scoring accepted phrase
                    final_candidates = [(p, s) for p, s in final_candidates if p != accepted_phrase]
                    break
            
            # Rule 2: If X is substring of X Y and both valid, keep X Y
            if is_substring_phrase(phrase, accepted_phrase):
                # Keep the longer phrase unless the shorter is whitelisted
                if phrase in WHITELIST and accepted_phrase not in WHITELIST:
                    # Remove the longer phrase, keep the whitelisted shorter one
                    final_candidates = [(p, s) for p, s in final_candidates if p != accepted_phrase]
                    break
                else:
                    keep_this = False
                    break
        
            # Rule 3: Handle specific near-duplicate patterns
            # If we have both "product design" and "product design senior", keep the longer one
            if (phrase == "product design" and accepted_phrase == "product design senior") or \
               (phrase == "product design senior" and accepted_phrase == "product design"):
                if len(phrase) > len(accepted_phrase):
                    # Remove the shorter one
                    final_candidates = [(p, s) for p, s in final_candidates if p != accepted_phrase]
                    break
                else:
                    keep_this = False
                    break
            
            # If we have both "senior" and "senior product", keep the longer one
            if (phrase == "senior" and accepted_phrase == "senior product") or \
               (phrase == "senior product" and accepted_phrase == "senior"):
                if len(phrase) > len(accepted_phrase):
                    # Remove the shorter one
                    final_candidates = [(p, s) for p, s in final_candidates if p != accepted_phrase]
                    break
                else:
                    keep_this = False
                    break
        
        if keep_this:
            final_candidates.append((phrase, score))
    
    return final_candidates

def extract_keywords(text: str, top_n: int = 30) -> Dict[str, Any]:
    """Extract meaningful keywords from text with improved normalization and filtering"""
    if not text or not text.strip():
        return {"keywords": [], "domain_tags": [], "role_tags": [], "dropped_examples": []}
    
    # Step 1: Normalize text and phrases
    normalized_text = normalize_text(text)
    normalized_text = normalize_phrases(normalized_text)
    words = normalized_text.split()
    
    # Step 2: Enhanced word normalization with proper lemmatization
    def lemmatize_word(word: str) -> str:
        """Improved lemmatization to handle common word forms without creating malformed words"""
        word_lower = word.lower()
        
        # Only apply lemmatization for specific patterns that we know are safe
        # Be very conservative to avoid creating malformed words
        
        # Handle clear verb forms - be very conservative
        if word_lower.endswith('ing') and len(word_lower) > 5:
            # Only for words we know are safe: designing -> design, testing -> test
            safe_ing_words = {
                'designing': 'design', 'testing': 'test', 'working': 'work', 'playing': 'play',
                'prototyping': 'prototype', 'developing': 'develop', 'creating': 'create',
                'building': 'build', 'making': 'make', 'using': 'use', 'learning': 'learn'
            }
            if word_lower in safe_ing_words:
                return safe_ing_words[word_lower]
        
        if word_lower.endswith('ed') and len(word_lower) > 4:
            # Only for words we know are safe: designed -> design, tested -> test
            safe_ed_words = {
                'designed': 'design', 'tested': 'test', 'worked': 'work', 'played': 'play',
                'developed': 'develop', 'created': 'create', 'built': 'build', 'made': 'make',
                'used': 'use', 'learned': 'learn', 'required': 'require'
            }
            if word_lower in safe_ed_words:
                return safe_ed_words[word_lower]
        
        if word_lower.endswith('ies') and len(word_lower) > 4:
            # studies -> study
            candidate = word_lower[:-3] + 'y'
            if len(candidate) >= 3:
                return candidate
        
        if word_lower.endswith('ied') and len(word_lower) > 4:
            # studied -> study
            candidate = word_lower[:-3] + 'y'
            if len(candidate) >= 3:
                return candidate
        
        # Handle specific noun forms carefully
        if word_lower.endswith('tion') and len(word_lower) > 5:
            # execution -> execute, but be careful
            candidate = word_lower[:-4] + 'e'
            if len(candidate) >= 4 and candidate not in ['execut', 'creat', 'implement']:
                return candidate
        
        if word_lower.endswith('sion') and len(word_lower) > 5:
            # decision -> decide
            candidate = word_lower[:-4] + 'e'
            if len(candidate) >= 4:
                return candidate
        
        # For most other cases, return the word as-is to avoid malformed results
        return word_lower
    
    # Step 3: Extract and normalize all potential keywords
    all_candidates = []
    
    # Extract single words with improved filtering
    for word in words:
        # Skip very short words unless they're domain-relevant acronyms
        if len(word) < 3:
            # Keep important acronyms
            if word.upper() in ['UX', 'UI', 'AI', 'API', 'CSS', 'HTML', 'JS', 'SQL', 'QA', 'KPI']:
                all_candidates.append(word.upper())
            continue
        
        # Skip blacklisted words
        if word.lower() in PHRASE_BLACKLIST or word.lower() in MINIMUM_SIGNAL_WORDS:
            continue
        
        # Skip company/brand names
        if is_company_brand_name(word):
            continue
        
        # Only keep skill/tool/method terms
        if not is_skill_tool_method(word):
            continue
        
        # Apply lemmatization
        normalized_word = lemmatize_word(word)
        if len(normalized_word) >= 3:
            all_candidates.append(normalized_word)
    
    # Extract meaningful bigrams
    for i in range(len(words) - 1):
        word1, word2 = words[i], words[i+1]
        
        # Skip if either word is too short or blacklisted
        if (len(word1) < 3 or len(word2) < 3 or
            word1.lower() in PHRASE_BLACKLIST or word2.lower() in PHRASE_BLACKLIST or
            word1.lower() in MINIMUM_SIGNAL_WORDS or word2.lower() in MINIMUM_SIGNAL_WORDS):
            continue
        
        # Skip if either word is a company/brand name
        if is_company_brand_name(word1) or is_company_brand_name(word2):
            continue
        
        # Create bigram
        bigram = f"{word1} {word2}"
        
        # Skip if bigram is blacklisted
        if bigram.lower() in PHRASE_BLACKLIST:
            continue
        
        # Only keep if both words are meaningful or bigram is whitelisted
        if (bigram.lower() in WHITELIST or 
            bigram.lower() in ALLOWED_PHRASES or
            (is_skill_tool_method(word1) and is_skill_tool_method(word2))):
            all_candidates.append(bigram.lower())
    
    # Extract meaningful trigrams
    for i in range(len(words) - 2):
        word1, word2, word3 = words[i], words[i+1], words[i+2]
        
        # Skip if any word is too short or blacklisted
        if (len(word1) < 3 or len(word2) < 3 or len(word3) < 3 or
            any(w.lower() in PHRASE_BLACKLIST for w in [word1, word2, word3]) or
            any(w.lower() in MINIMUM_SIGNAL_WORDS for w in [word1, word2, word3])):
            continue
        
        # Skip if any word is a company/brand name
        if any(is_company_brand_name(w) for w in [word1, word2, word3]):
            continue
        
        # Create trigram
        trigram = f"{word1} {word2} {word3}"
        
        # Skip if trigram is blacklisted
        if trigram.lower() in PHRASE_BLACKLIST:
            continue
        
        # Only keep if trigram is whitelisted or all words are meaningful
        if (trigram.lower() in WHITELIST or 
            trigram.lower() in ALLOWED_PHRASES or
            all(is_skill_tool_method(w) for w in [word1, word2, word3])):
            all_candidates.append(trigram.lower())
    
    # Step 4: Add whitelist phrases that appear in the text
    for phrase in WHITELIST:
        if phrase in normalized_text:
            all_candidates.append(phrase)
    
    # Step 5: Count frequencies and apply TF-IDF-like scoring
    word_counts = Counter(all_candidates)
    total_words = len(all_candidates)
    
    # Step 6: Score candidates using improved TF-IDF-like scoring
    scored_candidates = []
    for candidate, count in word_counts.most_common():
        # Base frequency score (normalized)
        frequency_score = min(count / max(total_words / 100, 1), 1.0)
        
        # Specificity bonus for multi-word phrases
        specificity_bonus = 0.3 if ' ' in candidate else 0.0
        
        # Length bonus for longer meaningful terms
        length_bonus = min(len(candidate) / 25.0, 0.2)
        
        # Whitelist bonus (high priority for whitelist items)
        whitelist_bonus = 0.4 if candidate in WHITELIST else 0.0
        
        # Domain relevance bonus
        domain_bonus = 0.2 if any(term in candidate for term in [
            'design', 'user', 'product', 'interface', 'experience', 'research', 'testing',
            'prototype', 'wireframe', 'usability', 'accessibility', 'analytics', 'data',
            'agile', 'scrum', 'collaboration', 'stakeholder', 'workflow', 'process'
        ]) else 0.0
        
        # Final score
        final_score = frequency_score + specificity_bonus + length_bonus + whitelist_bonus + domain_bonus
        scored_candidates.append((candidate, min(final_score, 1.0)))
    
    # Step 7: Sort by score and apply deduplication
    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    deduplicated_candidates = deduplicate_keywords_advanced(scored_candidates)
    
    # Step 8: Final quality filtering with malformed word detection
    final_candidates = []
    for candidate, score in deduplicated_candidates:
        # Skip if any word in the candidate is blacklisted
        words_in_candidate = candidate.split()
        has_blacklisted_word = any(word.lower() in PHRASE_BLACKLIST for word in words_in_candidate)
        
        # Additional check for malformed words (words that look broken)
        is_malformed = False
        for word in words_in_candidate:
            word_lower = word.lower()
            # Check for common malformed patterns
            if (word_lower.endswith('u') and len(word_lower) == 5 and word_lower not in ['value', 'issue']) or \
               (word_lower.endswith('e') and len(word_lower) == 6 and word_lower not in ['create', 'design', 'manage']) or \
               (word_lower.endswith('ie') and len(word_lower) == 7) or \
               (word_lower.endswith('c') and len(word_lower) == 6) or \
               (word_lower in ['statu', 'companie', 'proces', 'experienc', 'countrie', 'covey', 'deel']):
                is_malformed = True
                break
        
        if not has_blacklisted_word and not is_malformed and len(candidate.strip()) > 0:
            final_candidates.append((candidate, score))
    
    # Step 9: Ensure we have exactly top_n keywords
    if len(final_candidates) < top_n:
        # If we don't have enough, try to extract more from whitelist
        for phrase in WHITELIST:
            if phrase not in [kw for kw, _ in final_candidates]:
                final_candidates.append((phrase, 0.5))  # Lower score for whitelist fallbacks
                if len(final_candidates) >= top_n:
                    break
    
    # Step 10: Extract domain and role tags
    domain_tags = extract_domain_tags(text)
    role_tags = extract_role_tags(text)
    
    # Step 11: Get dropped examples for debugging
    dropped_examples = []
    for word in words[:50]:  # Check first 50 words
        if (len(word) < 3 or 
            word.lower() in MINIMUM_SIGNAL_WORDS or 
            word.lower() in PHRASE_BLACKLIST):
            dropped_examples.append(word)
            if len(dropped_examples) >= 10:
                break
    
    # Step 12: Return results
    return {
        "keywords": final_candidates[:top_n],
        "domain_tags": domain_tags,
        "role_tags": role_tags,
        "dropped_examples": dropped_examples
    }

def match_keywords_to_resume(jd_keywords: List[str], resume_text: str) -> Dict[str, List[str]]:
    """Match JD keywords against resume text"""
    normalized_resume = normalize_text(resume_text)
    
    matched = []
    missing = []
    
    for keyword, _ in jd_keywords:
        # Check for exact match
        if keyword in normalized_resume:
            matched.append(keyword)
        else:
            # Check for word-by-word match for multi-word phrases
            if ' ' in keyword:
                words = keyword.split()
                all_words_found = all(word in normalized_resume for word in words)
                if all_words_found:
                    matched.append(keyword)
                else:
                    missing.append(keyword)
            else:
                missing.append(keyword)
    
    return {
        "matched_keywords": matched,
        "missing_keywords": missing[:7]  # Top 7 missing keywords
    }

def generate_bullet_suggestions(missing_keywords: List[str], resume_text: str = "", all_jd_keywords: List[str] = []) -> List[str]:
    """Generate smart, natural resume bullets with intelligent keyword integration"""
    # Using smart bullet suggestion system
    
    # Normalize resume text for keyword checking
    resume_lower = resume_text.lower() if resume_text else ""
    
    # Filter out meaningless/filler words and words already in resume
    def is_meaningful_keyword(keyword):
        keyword_lower = keyword.lower()
        
        # Quick filler word check (most common ones first)
        if keyword_lower in {"bring", "truly", "ensuring", "making", "getting", "having", "being", "doing", "going", "very", "really", "quite", "rather", "things", "stuff", "ways", "methods", "initiatives", "outcomes", "results"}:
            return False
            
        # Check if already in resume (optimized)
        if keyword_lower in resume_words:
            return False
            
        # Check for singular/plural variations
        if keyword_lower.endswith('s') and keyword_lower[:-1] in resume_words:
            return False
        if not keyword_lower.endswith('s') and f"{keyword_lower}s" in resume_words:
            return False
            
        return True
    
    # Filter keywords to only meaningful ones not in resume
    meaningful_keywords = [kw for kw in missing_keywords if is_meaningful_keyword(kw)]
    
    # Add low-visibility words from all JD keywords (present <2 times in resume)
    if all_jd_keywords:
        for kw in all_jd_keywords:
            if kw not in meaningful_keywords and is_meaningful_keyword(kw):
                # Count occurrences in resume
                count = resume_lower.count(kw.lower())
                if count < 2:  # Low visibility
                    meaningful_keywords.append(kw)
    
    # Group keywords by semantic theme for better integration (cached for performance)
    keyword_themes = {
        "design_ux": ["figma", "design", "ui", "ux", "wireframes", "prototyping", "accessibility", "usability", "user experience", "user interface", "visual design", "interaction design"],
        "development": ["python", "javascript", "react", "node", "typescript", "api", "microservices", "docker", "kubernetes", "programming", "coding", "development", "software"],
        "infrastructure": ["aws", "cloud", "ci/cd", "devops", "monitoring", "security", "performance", "scalability", "deployment", "infrastructure", "serverless"],
        "data_analytics": ["analytics", "metrics", "kpi", "roi", "data", "science", "machine learning", "ai", "intelligence", "reporting", "dashboard", "insights"],
        "process_methodology": ["agile", "scrum", "kanban", "project management", "collaboration", "automation", "testing", "qa", "methodology", "workflow", "process"],
        "business_strategy": ["strategy", "stakeholder", "management", "budget", "improvement", "change", "training", "business", "stakeholder management", "strategic"]
    }
    
    # Smart bullet patterns with natural sentence structures
    bullet_patterns = [
        # Pattern 1: Action → Specific Implementation → Measurable Result
        {
            "verbs": ["Automated", "Redesigned", "Streamlined", "Launched"],
            "templates": [
                "Automated {specific_action}, reducing {concrete_metric} by {realistic_percent}% and {positive_outcome}",
                "Redesigned {specific_system} after {research_method}, increasing {concrete_metric} from {old_value}% to {new_value}%",
                "Streamlined {specific_process} using {technical_approach}, cutting {concrete_metric} by {realistic_percent}% and {positive_outcome}",
                "Launched {specific_solution} across {scope} {artifacts}, reducing {concrete_metric} by {realistic_percent}% and {positive_outcome}"
            ]
        },
        
        # Pattern 2: Partnership → Technical Achievement → Business Impact
        {
            "verbs": ["Partnered", "Collaborated", "Worked", "Teamed"],
            "templates": [
                "Partnered with {team} to {specific_achievement}, preventing {negative_outcome} and {positive_outcome}",
                "Collaborated on {specific_project} that {technical_benefit}, reducing {concrete_metric} by {realistic_percent}% and {business_benefit}",
                "Worked with {team} to {specific_action}, cutting {concrete_metric} by {realistic_percent}% and {positive_outcome}",
                "Teamed with {team} to {specific_implementation}, improving {concrete_metric} by {realistic_percent}% and {positive_outcome}"
            ]
        },
        
        # Pattern 3: Leadership → Technical Innovation → Measurable Impact
        {
            "verbs": ["Led", "Championed", "Directed", "Spearheaded"],
            "templates": [
                "Led {specific_initiative} that {technical_achievement}, reducing {concrete_metric} by {realistic_percent}% and {positive_outcome}",
                "Championed {specific_standard} implementation, cutting {concrete_metric} by {realistic_percent}% and {business_benefit}",
                "Directed {specific_project} using {technical_approach}, improving {concrete_metric} by {realistic_percent}% and {positive_outcome}",
                "Spearheaded {specific_effort} that {technical_benefit}, reducing {concrete_metric} by {realistic_percent}% and {business_impact}"
            ]
        },
        
        # Pattern 4: Problem → Solution → Measurable Outcome
        {
            "verbs": ["Identified", "Solved", "Addressed", "Eliminated"],
            "templates": [
                "Identified {specific_problem} and {solution_action}, reducing {concrete_metric} by {realistic_percent}% and {positive_outcome}",
                "Solved {specific_challenge} through {technical_method}, cutting {concrete_metric} by {realistic_percent}% and {business_benefit}",
                "Addressed {specific_issue} with {technical_approach}, improving {concrete_metric} by {realistic_percent}% and {positive_outcome}",
                "Eliminated {specific_bottleneck} by {solution_action}, reducing {concrete_metric} by {realistic_percent}% and {positive_outcome}"
            ]
        },
        
        # Pattern 5: Innovation → Technical Implementation → Business Value
        {
            "verbs": ["Introduced", "Developed", "Created", "Built"],
            "templates": [
                "Introduced {specific_innovation} that {technical_benefit}, reducing {concrete_metric} by {realistic_percent}% and {positive_outcome}",
                "Developed {specific_solution} using {technical_approach}, cutting {concrete_metric} by {realistic_percent}% and {business_benefit}",
                "Created {specific_system} that {technical_achievement}, improving {concrete_metric} by {realistic_percent}% and {positive_outcome}",
                "Built {specific_tool} for {specific_purpose}, reducing {concrete_metric} by {realistic_percent}% and {business_impact}"
            ]
        }
    ]
    
    # Smart keyword integration function
    def find_theme_for_keyword(keyword):
        """Find the best theme for a keyword"""
        keyword_lower = keyword.lower()
        for theme, keywords in keyword_themes.items():
            if any(theme_kw in keyword_lower for theme_kw in keywords):
                return theme
        return None
    
    def get_contextual_keyword_for_theme(theme, available_keywords):
        """Get a keyword that fits the theme contextually"""
        if not available_keywords:
            return None
        theme_keywords = keyword_themes.get(theme, [])
        for kw in available_keywords:
            if any(theme_kw in kw.lower() for theme_kw in theme_keywords):
                return kw
        return None
    
    # Realistic metrics and concrete terms
    realistic_percentages = [10, 15, 20, 25, 30, 40, 50, 60, 75, 80, 90, 95]
    concrete_metrics = [
        "manual prep time", "approval cycles", "deployment time", "user activation rate", 
        "code review time", "bug resolution time", "onboarding duration", "response time",
        "error rate", "adoption rate", "cycle time", "processing time", "delivery time"
    ]
    positive_outcomes = [
        "preventing production issues", "improving user satisfaction", "reducing manual errors",
        "enhancing team productivity", "accelerating delivery", "boosting reliability",
        "streamlining workflows", "increasing efficiency", "reducing costs", "improving quality",
        "enhancing user experience", "reducing support tickets", "accelerating time-to-market"
    ]
    business_benefits = [
        "reducing support tickets", "improving user retention", "accelerating time-to-market",
        "enhancing team efficiency", "reducing operational costs", "improving quality"
    ]
    technical_benefits = [
        "reduced manual effort", "improved consistency", "enhanced performance",
        "increased reliability", "better user experience", "streamlined workflows"
    ]
    
    def generate_smart_bullet(pattern_idx, theme, keyword=None):
        """Generate a single smart, natural bullet"""
        print(f"🔧 DEBUG: generate_smart_bullet called with keyword='{keyword}', theme='{theme}'")
        pattern = bullet_patterns[pattern_idx]
        template = random.choice(pattern["templates"])
        
        # Generate realistic metrics
        percent = random.choice(realistic_percentages)
        metric = random.choice(concrete_metrics)
        outcome = random.choice(positive_outcomes)
        business_benefit = random.choice(business_benefits)
        technical_benefit = random.choice(technical_benefits)
        
        # Theme-specific concrete terms
        theme_specifics = {
            "design_ux": {
                "actions": ["design system implementation", "usability testing", "accessibility audits", "user research"],
                "systems": ["design system", "UI component library", "user interface", "interaction design"],
                "processes": ["user onboarding flow", "design handoff process", "usability testing protocol"],
                "innovations": ["design tokens", "component library", "style guide", "user experience framework"],
                "standards": ["WCAG AA compliance", "accessibility guidelines", "design system standards"],
                "artifacts": ["screens", "components", "interfaces", "prototypes"]
            },
            "development": {
                "actions": ["API development", "automated testing", "code review process", "microservices implementation"],
                "systems": ["API gateway", "microservices architecture", "containerized services", "automated test suite"],
                "processes": ["code review process", "deployment pipeline", "testing workflow", "development process"],
                "innovations": ["API endpoints", "automated tests", "microservices", "containerized applications"],
                "standards": ["API design standards", "code quality standards", "testing protocols"],
                "artifacts": ["endpoints", "services", "applications", "test cases"]
            },
            "infrastructure": {
                "actions": ["CI/CD pipeline setup", "monitoring implementation", "security hardening", "performance optimization"],
                "systems": ["CI/CD pipeline", "monitoring dashboard", "deployment automation", "security protocols"],
                "processes": ["deployment process", "monitoring workflow", "security audit process"],
                "innovations": ["deployment automation", "monitoring dashboard", "security protocols", "performance profiling"],
                "standards": ["security standards", "deployment protocols", "monitoring guidelines"],
                "artifacts": ["pipelines", "dashboards", "services", "infrastructure"]
            },
            "data_analytics": {
                "actions": ["data analysis", "reporting automation", "dashboard creation", "performance tracking"],
                "systems": ["analytics dashboard", "data pipeline", "reporting system", "performance metrics"],
                "processes": ["data analysis process", "reporting workflow", "performance monitoring"],
                "innovations": ["analytics dashboard", "data pipeline", "reporting automation", "performance metrics"],
                "standards": ["data quality standards", "reporting protocols", "analytics guidelines"],
                "artifacts": ["dashboards", "reports", "metrics", "insights"]
            },
            "process_methodology": {
                "actions": ["agile implementation", "collaboration framework", "workflow optimization", "process improvement"],
                "systems": ["collaboration framework", "workflow system", "process management", "quality gates"],
                "processes": ["collaboration process", "workflow management", "quality assurance process"],
                "innovations": ["collaboration framework", "workflow optimization", "process improvement"],
                "standards": ["agile standards", "collaboration protocols", "quality guidelines"],
                "artifacts": ["processes", "workflows", "frameworks", "methodologies"]
            },
            "business_strategy": {
                "actions": ["strategic planning", "stakeholder management", "change management", "budget optimization"],
                "systems": ["strategic planning system", "stakeholder management", "change management process"],
                "processes": ["strategic planning process", "stakeholder engagement", "change management"],
                "innovations": ["strategic framework", "stakeholder management", "change management"],
                "standards": ["strategic standards", "stakeholder protocols", "change guidelines"],
                "artifacts": ["strategies", "plans", "frameworks", "processes"]
            }
        }
        
        # Get theme-specific terms
        theme_terms = theme_specifics.get(theme, theme_specifics["development"])
        
        # Fill template with smart, contextual values
        replacements = {
            "specific_action": random.choice(theme_terms["actions"]),
            "specific_system": random.choice(theme_terms["systems"]),
            "specific_process": random.choice(theme_terms["processes"]),
            "specific_innovation": random.choice(theme_terms["innovations"]),
            "specific_standard": random.choice(theme_terms["standards"]),
            "specific_project": random.choice(theme_terms["actions"]),
            "specific_initiative": random.choice(theme_terms["actions"]),
            "specific_achievement": random.choice(theme_terms["actions"]),
            "specific_implementation": random.choice(theme_terms["actions"]),
            "specific_solution": random.choice(theme_terms["innovations"]),
            "specific_tool": random.choice(theme_terms["innovations"]),
            "specific_purpose": random.choice(theme_terms["actions"]),
            "specific_problem": random.choice([
                "performance bottlenecks", "deployment failures", "user confusion", "manual errors",
                "accessibility issues", "security vulnerabilities", "process inefficiencies"
            ]),
            "specific_challenge": random.choice([
                "scalability issues", "user experience problems", "security concerns", "performance gaps",
                "accessibility barriers", "process bottlenecks", "integration challenges"
            ]),
            "specific_issue": random.choice([
                "user experience issues", "performance problems", "security gaps", "accessibility barriers",
                "process inefficiencies", "integration challenges", "deployment issues"
            ]),
            "specific_bottleneck": random.choice([
                "deployment bottlenecks", "user onboarding delays", "code review backlogs", "testing bottlenecks",
                "approval process delays", "integration bottlenecks", "performance bottlenecks"
            ]),
            "solution_action": random.choice(theme_terms["actions"]),
            "technical_method": random.choice(theme_terms["actions"]),
            "technical_approach": random.choice(theme_terms["actions"]),
            "research_method": random.choice([
                "usability testing", "user research", "performance analysis", "accessibility audit",
                "stakeholder interviews", "data analysis", "user feedback analysis"
            ]),
            "team": random.choice([
                "engineering", "design", "product", "QA", "marketing", "data science", "stakeholders"
            ]),
            "scope": random.choice(["5+", "8+", "10+", "15+", "20+", "25+", "50+", "100+", "500+"]),
            "artifacts": random.choice(theme_terms["artifacts"]),
            "concrete_metric": metric,
            "realistic_percent": percent,
            "old_value": random.choice([45, 50, 55, 60, 65, 70, 75]),
            "new_value": random.choice([80, 85, 90, 95, 98]),
            "positive_outcome": outcome,
            "business_benefit": business_benefit,
            "technical_benefit": technical_benefit,
            "technical_achievement": random.choice(theme_terms["actions"]),
            "business_impact": random.choice([
                "faster delivery cycles", "improved user experience", "reduced operational costs",
                "enhanced team productivity", "better stakeholder satisfaction", "increased reliability"
            ]),
            "negative_outcome": random.choice([
                "production issues", "user complaints", "security vulnerabilities", "performance degradation",
                "accessibility violations", "deployment failures", "manual errors"
            ]),
            "specific_effort": random.choice(theme_terms["actions"])
        }
        
        # Integrate keyword naturally if provided with medium weight formatting
        if keyword:
            # Format keyword with medium weight
            formatted_keyword = f"<span style='font-weight: 500;'>{keyword}</span>"
            
            # Simple keyword integration - replace the first available placeholder
            if "specific_initiative" in replacements:
                replacements["specific_initiative"] = f"{formatted_keyword} initiative"
            elif "specific_system" in replacements:
                replacements["specific_system"] = f"{formatted_keyword} system"
            elif "specific_solution" in replacements:
                replacements["specific_solution"] = f"{formatted_keyword} solution"
            elif "specific_tool" in replacements:
                replacements["specific_tool"] = f"{formatted_keyword} tool"
            elif "specific_project" in replacements:
                replacements["specific_project"] = f"{formatted_keyword} project"
            elif "specific_standard" in replacements:
                replacements["specific_standard"] = f"{formatted_keyword} standard"
            elif "specific_innovation" in replacements:
                replacements["specific_innovation"] = f"{formatted_keyword} innovation"
            elif "specific_process" in replacements:
                replacements["specific_process"] = f"{formatted_keyword} process"
            elif "technical_approach" in replacements:
                replacements["technical_approach"] = f"{formatted_keyword} approach"
            elif "specific_effort" in replacements:
                replacements["specific_effort"] = f"{formatted_keyword} effort"
            else:
                # If no specific placeholder, add keyword to the beginning
                template = f"Implemented {formatted_keyword} " + template.lower()
        
        # Fill the template
        try:
            bullet = template.format(**replacements)
            return bullet
        except KeyError as e:
            print(f"🔧 DEBUG: Template formatting error: {e}")
            return f"Improved {theme} processes, increasing efficiency by {percent}% and {outcome}"
    
    # Generate 4-5 smart bullets with different patterns
    suggestions = []
    used_verbs = set()
    used_keywords = set()
    
    # Generate bullets with smart keyword integration - ONLY with keywords
    # Only generate bullets if we have keywords
    if not meaningful_keywords:
        return ["No relevant keywords found for bullet suggestions"]
    
    # Generate exactly 4 bullets, each with a keyword
    for i in range(min(4, len(meaningful_keywords))):  # Exactly 4 bullets, each with keyword
        # Choose a different pattern for each bullet
        pattern_idx = i % len(bullet_patterns)
        
        # Find a theme and keyword for this bullet
        theme = None
        keyword = None
        
        # Use a meaningful keyword (prioritize unused ones)
        if meaningful_keywords and len(used_keywords) < len(meaningful_keywords):
            for kw in meaningful_keywords:
                if kw not in used_keywords:
                    theme = find_theme_for_keyword(kw)
                    if theme:
                        keyword = kw
                        used_keywords.add(kw)
                        break
        
        # If no unused keyword found, reuse a keyword
        if not keyword and meaningful_keywords:
            keyword = random.choice(meaningful_keywords)
            theme = find_theme_for_keyword(keyword)
            if not theme:
                theme = random.choice(list(keyword_themes.keys()))
        
        # Generate the bullet (guaranteed to have a keyword)
        bullet = generate_smart_bullet(pattern_idx, theme, keyword)
        
        # Ensure no duplicate starting verbs
        verb = bullet.split()[0]
        if verb in used_verbs:
            # Try a different pattern
            for alt_pattern in range(len(bullet_patterns)):
                if alt_pattern != pattern_idx:
                    alt_bullet = generate_smart_bullet(alt_pattern, theme, keyword)
                    alt_verb = alt_bullet.split()[0]
                    if alt_verb not in used_verbs:
                        bullet = alt_bullet
                        break
        
        used_verbs.add(bullet.split()[0])
        suggestions.append(bullet)
    
    return suggestions[:4]  # Return exactly 4 bullets

def calculate_scores(matched_keywords: List[str], all_keywords: List[str], 
                    resume_text: str, jd_text: str) -> Dict[str, float]:
    """Calculate various scores for the analysis"""
    if not all_keywords:
        return {"ats_score": 0, "text_similarity": 0, "keyword_coverage": 0}
    
    # ATS Match Score (0-100)
    keyword_coverage = len(matched_keywords) / len(all_keywords) * 100
    ats_score = min(keyword_coverage * 1.2, 100)  # Boost score slightly
    
    # Text Similarity (0-100)
    # Simple word overlap calculation
    resume_words = set(normalize_text(resume_text).split())
    jd_words = set(normalize_text(jd_text).split())
    
    if jd_words:
        common_words = resume_words.intersection(jd_words)
        text_similarity = len(common_words) / len(jd_words) * 100
    else:
        text_similarity = 0
    
    return {
        "ats_score": round(ats_score, 1),
        "text_similarity": round(text_similarity, 1),
        "keyword_coverage": round(keyword_coverage, 1)
    }

def extract_text_from_file(file_content: bytes, filename: str, content_type: str) -> tuple[str, dict]:
    """
    Extract text from various file formats and determine ATS compatibility.
    Returns (extracted_text, file_info_dict)
    """
    import io
    import mimetypes
    from pathlib import Path
    
    file_info = {
        "filename": filename,
        "content_type": content_type,
        "size": len(file_content),
        "ats_compatible": False,
        "text_extractable": False,
        "file_type": "unknown",
        "extraction_method": "none",
        "error": None
    }
    
    try:
        # Determine file type
        file_extension = Path(filename).suffix.lower() if filename else ""
        
        # Handle different file types
        if file_extension == ".txt" or content_type == "text/plain":
            file_info["file_type"] = "text"
            file_info["ats_compatible"] = True
            file_info["text_extractable"] = True
            file_info["extraction_method"] = "direct_decode"
            
            # Try to decode as text
            try:
                text = file_content.decode('utf-8')
                if len(text.strip()) > 10:  # Ensure there's actual content
                    return text, file_info
                else:
                    file_info["error"] = "File appears to be empty or contains only whitespace"
                    return "", file_info
            except UnicodeDecodeError:
                file_info["error"] = "File is not valid UTF-8 text"
                return "", file_info
                
        elif file_extension == ".pdf" or content_type == "application/pdf":
            file_info["file_type"] = "pdf"
            file_info["extraction_method"] = "pdf_parser"
            
            try:
                # Try to extract text from PDF
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                
                text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        # DO NOT normalize whitespace - preserve raw text for preflight
                        text += page_text + "\n"
                
                # Log whitespace debug if enabled
                log_whitespace_debug(text, "PDF_EXTRACTION")
                
                if len(text.strip()) > 50:  # PDF has extractable text
                    file_info["ats_compatible"] = True
                    file_info["text_extractable"] = True
                    return text.strip(), file_info
                else:
                    # PDF might be image-based (scanned)
                    file_info["ats_compatible"] = False
                    file_info["text_extractable"] = False
                    file_info["error"] = "PDF appears to be image-based (scanned document). ATS systems cannot read scanned PDFs. Please use a text-based PDF or convert to .txt format."
                    return "", file_info
                    
            except ImportError:
                file_info["error"] = "PDF processing not available. Please convert to .txt format."
                return "", file_info
            except Exception as e:
                file_info["error"] = f"Error processing PDF: {str(e)}"
                return "", file_info
                
        elif file_extension in [".doc", ".docx"] or content_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            file_info["file_type"] = "word"
            file_info["extraction_method"] = "word_parser"
            
            try:
                if file_extension == ".docx":
                    import zipfile
                    import xml.etree.ElementTree as ET
                    
                    # Extract text from DOCX
                    with zipfile.ZipFile(io.BytesIO(file_content)) as docx:
                        # Read the main document
                        xml_content = docx.read('word/document.xml')
                        root = ET.fromstring(xml_content)
                        
                        # Extract text from all text nodes
                        text = ""
                        for elem in root.iter():
                            if elem.text:
                                text += elem.text + " "
                        
                        if len(text.strip()) > 50:
                            file_info["ats_compatible"] = True
                            file_info["text_extractable"] = True
                            return text.strip(), file_info
                        else:
                            file_info["error"] = "Word document appears to be empty or contains only formatting"
                            return "", file_info
                else:
                    file_info["error"] = "Legacy .doc format not supported. Please save as .docx or .txt format."
                    return "", file_info
                    
            except Exception as e:
                file_info["error"] = f"Error processing Word document: {str(e)}"
                return "", file_info
                
        else:
            file_info["error"] = f"Unsupported file format: {file_extension or content_type}. Supported formats: .txt, .pdf, .docx"
            return "", file_info
            
    except Exception as e:
        file_info["error"] = f"Unexpected error processing file: {str(e)}"
        return "", file_info

@app.post("/analyze")
async def analyze_resume(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """Main endpoint for resume analysis"""
    try:
        # Validation
        if not job_description or len(job_description.strip()) < 10:
            raise HTTPException(status_code=400, detail="Job description must be at least 10 characters")
        
        if not resume_file:
            raise HTTPException(status_code=400, detail="Resume file is required")
        
        # Process resume file with deterministic preflight check
        resume_content = await resume_file.read()
        
        # Log binary integrity at ingress (reduced logging for performance)
        # log_file_integrity("INGRESS", resume_content, resume_file.filename)
        
        # Use deterministic preflight system if available
        if PREFLIGHT_AVAILABLE:  # Re-enabled for production
            # logger.info("=== USING DETERMINISTIC PREFLIGHT SYSTEM ===")
            try:
                # Log binary integrity before preflight (reduced logging for performance)
                # log_file_integrity("PREFLIGHT_START", resume_content, resume_file.filename)
                
                # logger.info(f"Calling preflight_document for {resume_file.filename}")
                preflight_result = preflight_document(resume_content, resume_file.filename)
                # logger.info(f"Preflight result: ok={preflight_result.ok}")
                
                if not preflight_result.ok:
                    # Preflight failed - return user-friendly error
                    # logger.info("Preflight failed - returning error")
                    return {
                        "status": "error",
                        "message": preflight_result.user_message,
                        "preflight_details": preflight_result.details.__dict__ if preflight_result.details else None
                    }
                else:
                    # logger.info("Preflight passed - proceeding with analysis")
                    # Use preflight system for text extraction
                    resume_text, file_info = extract_text_with_preflight(resume_content, resume_file.filename, resume_file.content_type)
            except Exception as e:
                logger.error(f"Error in preflight system: {e}")
                # Fallback to old system if preflight fails
                resume_text, file_info = extract_text_from_file(resume_content, resume_file.filename, resume_file.content_type)
        else:
            # Fallback to old system if preflight not available
            resume_text, file_info = extract_text_from_file(resume_content, resume_file.filename, resume_file.content_type)
        
        # Check if file processing was successful
        if file_info["error"]:
            return {
                "status": "error",
                "message": file_info["error"],
                "file_info": file_info,
                "ats_compatible": file_info["ats_compatible"],
                "text_extractable": file_info["text_extractable"]
            }
        
        if not file_info["text_extractable"]:
            return {
                "status": "error",
                "message": "Unable to extract text from the uploaded file. Please ensure the file is ATS-compatible.",
                "file_info": file_info,
                "ats_compatible": file_info["ats_compatible"],
                "text_extractable": file_info["text_extractable"]
            }
        
        if len(resume_text.strip()) < 50:
            return {
                "status": "error",
                "message": "The uploaded file contains very little text. Please ensure your resume has sufficient content for analysis.",
                "file_info": file_info,
                "ats_compatible": file_info["ats_compatible"],
                "text_extractable": file_info["text_extractable"]
            }
        
        # Extract keywords from job description using smart extractor if available
        if smart_extractor:
            # logger.info("=== USING SMART KEYWORD EXTRACTOR ===")
            # logger.info(f"Job description length: {len(job_description)}")
            jd_keywords_list = smart_extractor.extract_smart_keywords(job_description, 30)
            # logger.info(f"Extracted {len(jd_keywords_list)} keywords: {jd_keywords_list[:10]}")
            jd_keywords = [(kw, 1.0) for kw in jd_keywords_list]  # Convert to expected format
            
            # Find matching keywords using smart extractor
            matched_keywords, missing_keywords = smart_extractor.find_matching_keywords(resume_text, jd_keywords_list)
            # logger.info(f"Found {len(matched_keywords)} matched keywords: {matched_keywords}")
            # logger.info(f"Found {len(missing_keywords)} missing keywords: {missing_keywords[:5]}")
            matching_result = {
                "matched_keywords": matched_keywords,
                "missing_keywords": missing_keywords[:7]  # Top 7 missing
            }
            
            # Create domain and role tags (simplified for smart extractor)
            domain_tags = []
            role_tags = []
            dropped_examples = []
            
        else:
            # logger.info("Using legacy keyword extractor")
            jd_result = extract_keywords(job_description, 30)
            jd_keywords = jd_result["keywords"]
            
            # Match keywords against resume
            matching_result = match_keywords_to_resume(jd_keywords, resume_text)
            
            # Extract additional data from legacy result
            domain_tags = jd_result["domain_tags"]
            role_tags = jd_result["role_tags"]
            dropped_examples = jd_result["dropped_examples"]
        
        # Generate bullet suggestions
        bullet_suggestions = generate_bullet_suggestions(
            matching_result["missing_keywords"], 
            resume_text, 
            [kw for kw, _ in jd_keywords]
        )
        
        # Calculate scores
        scores = calculate_scores(
            matching_result["matched_keywords"], 
            [kw for kw, score in jd_keywords], 
            resume_text, 
            job_description
        )
        
        # DEBUG: Log the response data structure (reduced for performance)
        # logger.info("=== BACKEND RESPONSE DEBUG ===")
        # logger.info(f"JD Keywords extracted: {len(jd_keywords)}")
        # logger.info(f"Matched keywords count: {len(matching_result['matched_keywords'])}")
        # logger.info(f"Missing keywords count: {len(matching_result['missing_keywords'])}")
        # logger.info(f"Top 7 missing keywords: {matching_result['missing_keywords'][:7]}")
        # logger.info(f"Bullet suggestions count: {len(bullet_suggestions)}")
        
        # Prepare response
        result = {
            "score": scores["ats_score"],
            "textSimilarity": scores["text_similarity"],
            "keywordCoverage": scores["keyword_coverage"],
            "all_keywords": [kw for kw, score in jd_keywords],  # Top 30 JD keywords
            "matched_keywords": matching_result["matched_keywords"],  # Present in resume
            "missing_keywords": matching_result["missing_keywords"],  # Top 7 missing
            "bullet_suggestions": bullet_suggestions,  # 4 bullet suggestions
            "domain_tags": domain_tags,
            "role_tags": role_tags,
            "dropped_examples": dropped_examples,
            "file_info": file_info,
            "message": "Analysis completed successfully!"
        }
        
        # Log the final response structure (reduced for performance)
        # logger.info(f"Final response - missing_keywords type: {type(result['missing_keywords'])}")
        # logger.info(f"Final response - missing_keywords length: {len(result['missing_keywords'])}")
        # logger.info(f"Final response - missing_keywords content: {result['missing_keywords']}")
        # logger.info("=== END BACKEND DEBUG ===")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/extract-keywords")
async def extract_keywords_endpoint(
    jd_text: str = Form(...),
    cv_text: str = Form(...)
) -> Dict[str, Any]:
    """Extract keywords and match against CV (legacy endpoint)"""
    try:
        # Validation
        if not jd_text.strip() or not cv_text.strip():
            raise HTTPException(status_code=400, detail="Both job description and CV text are required")
        
        # Extract keywords from job description
        jd_result = extract_keywords(jd_text, 30)
        jd_keywords = jd_result["keywords"]
        
        # Match keywords against CV
        matching_result = match_keywords_to_resume(jd_keywords, cv_text)
        
        # Generate bullet suggestions
        print("🔧 DEBUG: About to call generate_bullet_suggestions")
        bullet_suggestions = generate_bullet_suggestions(
            matching_result["missing_keywords"], 
            cv_text, 
            [kw for kw, _ in jd_keywords]
        )
        print(f"🔧 DEBUG: Generated {len(bullet_suggestions)} bullet suggestions")
        
        # Calculate scores
        scores = calculate_scores(
            matching_result["matched_keywords"], 
            [kw for kw, _ in jd_keywords], 
            cv_text, 
            jd_text
        )
        
        # DEBUG: Log the response data structure
        logger.info("=== EXTRACT-KEYWORDS DEBUG ===")
        logger.info(f"JD Keywords extracted: {len(jd_keywords)}")
        logger.info(f"Matched keywords count: {len(matching_result['matched_keywords'])}")
        logger.info(f"Missing keywords count: {len(matching_result['missing_keywords'])}")
        logger.info(f"Top 7 missing keywords: {matching_result['missing_keywords'][:7]}")
        logger.info(f"Bullet suggestions count: {len(bullet_suggestions)}")
        
        result = {
            "all_keywords": [kw for kw, score in jd_keywords],
            "matched_keywords": matching_result["matched_keywords"],
            "missing_keywords": matching_result["missing_keywords"],
            "bullet_suggestions": bullet_suggestions,
            "score": scores["ats_score"],
            "textSimilarity": scores["text_similarity"],
            "keywordCoverage": scores["keyword_coverage"],
            "domain_tags": jd_result["domain_tags"],
            "role_tags": jd_result["role_tags"],
            "dropped_examples": jd_result["dropped_examples"]
        }
        
        # Log the final response structure
        logger.info(f"Final response - missing_keywords type: {type(result['missing_keywords'])}")
        logger.info(f"Final response - missing_keywords length: {len(result['missing_keywords'])}")
        logger.info(f"Final response - missing_keywords content: {result['missing_keywords']}")
        logger.info("=== END EXTRACT-KEYWORDS DEBUG ===")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Keyword extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Keyword extraction failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "ATS Resume Checker API v2.0 is running!"}

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "message": "API is working!",
        "version": "2.1.2",
        "smart_extractor_available": SMART_EXTRACTOR_AVAILABLE,
        "smart_extractor_initialized": smart_extractor is not None,
        "deterministic_preflight_available": PREFLIGHT_AVAILABLE
    }

@app.get("/debug")
async def debug():
    import os
    import sys
    try:
        from deterministic_preflight import preflight_document
        preflight_import = "SUCCESS"
    except Exception as e:
        preflight_import = f"FAILED: {str(e)}"
    
    return {
        "version": "2.1.2",
        "python_version": sys.version,
        "current_dir": os.getcwd(),
        "files_in_dir": os.listdir("."),
        "preflight_import": preflight_import,
        "environment": os.environ.get("ENVIRONMENT", "unknown")
    }

@app.get("/test")
async def test_interface():
    """Serve the test interface HTML"""
    try:
        with open("test_interface.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return {"error": "Test interface not found"}

@app.get("/test-extractor")
async def test_extractor():
    """Test the smart extractor directly"""
    if not smart_extractor:
        return {"error": "Smart extractor not available"}
    
    test_jd = "We are looking for a Software Engineer with strong Python skills and experience in web development."
    keywords = smart_extractor.extract_smart_keywords(test_jd, 10)
    
    return {
        "test_jd": test_jd,
        "keywords": keywords,
        "extractor_type": type(smart_extractor).__name__,
        "smart_extractor_available": SMART_EXTRACTOR_AVAILABLE
    }

@app.get("/simple")
async def simple_test():
    """Serve the simple test interface HTML"""
    try:
        with open("simple_test.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return {"error": "Simple test interface not found"}

@app.get("/upload")
async def file_upload_test():
    """Serve the file upload test interface HTML"""
    try:
        with open("simple_file_upload.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return {"error": "File upload test interface not found"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting ATS Checker API v2.0 on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
