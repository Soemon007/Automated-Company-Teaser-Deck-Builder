import re
import warnings

# Try importing Presidio (fallback if not installed)
try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import OperatorConfig
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False
    warnings.warn("Presidio libraries not found. Falling back to Regex. Install 'presidio-analyzer' & 'presidio-anonymizer'.")

# Global engines (Singleton pattern)
_analyzer = None
_anonymizer = None

def get_engines():
    global _analyzer, _anonymizer
    if _analyzer is None:
        _analyzer = AnalyzerEngine()
    if _anonymizer is None:
        _anonymizer = AnonymizerEngine()
    return _analyzer, _anonymizer

def check_anonymization(data):
    """
    Recursively cleans Strings, Lists, and Dictionaries.
    """
    if isinstance(data, str):
        return sanitize_string(data)
    
    if isinstance(data, list):
        return [check_anonymization(item) for item in data]
        
    if isinstance(data, dict):
        # Keys to skip anonymization
        SKIP_KEYS = {"icons", "certifications", "highlight_images", "source_urls", "url"}
        
        return {
            key: (value if key in SKIP_KEYS else check_anonymization(value))
            for key, value in data.items()
        }
    
    return data

def sanitize_string(text):
    # 1. First run Regex Fallback to catch obvious patterns (Works even if Presidio is off)
    #    We run this FIRST to catch specific phrases like "Headquartered in Pune" 
    #    before the NLP breaks them apart.
    text = sanitize_fallback(text)

    if PRESIDIO_AVAILABLE:
        try:
            analyzer, anonymizer = get_engines()
            
            # --- Target Specific Entities Only ---
            # ORG: Companies | GPE: Countries/Cities | PERSON: Names
            # IGNORE 'DATE' and 'MONEY' because teasers need those numbers
            results = analyzer.analyze(
                text=text,
                language='en',
                entities=["ORG", "PERSON"],
                score_threshold=0.5
            )
            
            # --- Investor-Speak Replacements ---
            # Instead of <ORG>, we use "The Company"
            operators = {
                "ORG": OperatorConfig("replace", {"new_value": "the Company"}),
                "PERSON": OperatorConfig("replace", {"new_value": "Key Management"}),
            }
            
            anonymized_result = anonymizer.anonymize(
                analyzer_results=results,
                text=text,
                operators=operators
            )
            
            return anonymized_result.text
            
        except Exception as e:
            # Fallback if Spacy model isn't downloaded
            print(f"⚠️ Presidio Error: {e}")
            return text
            
    return text

def sanitize_fallback(text):
    # Dynamic Pattern Replacement
    regex_rules = [
        # 1. Remove Corporate Suffixes (Case Insensitive)
        (r"(?i)\b(pvt\.?|ltd\.?|limited|inc\.?|corp\.?|llc)\b", ""),
        
        # 4. Catch Founders/names often missed
        (r"(?i)founded by [A-Z][a-z]+", "founded by industry veterans"),
    ]

    sanitized = text
    for pattern, replacement in regex_rules:
        sanitized = re.sub(pattern, replacement, sanitized)
        
    return sanitized
