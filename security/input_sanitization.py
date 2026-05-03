# Layer 3: Input Sanitization - Detect malicious patterns
from typing import Tuple
from config import MALICIOUS_KEYWORDS
import re

class InputSanitizer:
    """Layer 3: Input Sanitization - Detect and block malicious patterns"""
    
    MALICIOUS_KEYWORDS = MALICIOUS_KEYWORDS
    
    # SQL injection patterns
    SQL_PATTERNS = [
        r"(\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|EXEC|EXECUTE)\b)",
        r"(--|;|/\*)",
        r"(\bOR\b.*=.*)",
        r"(xp_|sp_)"
    ]
    
    # Prompt injection patterns
    PROMPT_INJECTION_PATTERNS = [
        r"ignore.*instruction",
        r"bypass.*rule",
        r"override.*setting",
        r"disable.*check",
        r"forget.*previous"
    ]
    
    @classmethod
    def check_malicious_keywords(cls, query: str) -> Tuple[bool, str, list]:
        """Check for malicious keywords"""
        query_lower = query.lower()
        found_keywords = []
        
        for keyword in cls.MALICIOUS_KEYWORDS:
            if keyword in query_lower:
                found_keywords.append(keyword)
        
        if found_keywords:
            return False, f"Malicious keywords detected: {', '.join(found_keywords)}", found_keywords
        
        return True, "No malicious keywords detected", []
    
    @classmethod
    def check_sql_injection(cls, query: str) -> Tuple[bool, str]:
        """Check for SQL injection patterns"""
        for pattern in cls.SQL_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return False, f"SQL injection pattern detected"
        
        return True, "No SQL injection detected"
    
    @classmethod
    def check_prompt_injection(cls, query: str) -> Tuple[bool, str]:
        """Check for prompt injection patterns"""
        for pattern in cls.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return False, f"Prompt injection pattern detected"
        
        return True, "No prompt injection detected"
    
    @classmethod
    def sanitize(cls, query: str) -> Tuple[bool, str]:
        """Full sanitization check"""
        # Check keywords
        is_safe, msg, _ = cls.check_malicious_keywords(query)
        if not is_safe:
            return False, msg
        
        # Check SQL injection
        is_safe, msg = cls.check_sql_injection(query)
        if not is_safe:
            return False, msg
        
        # Check prompt injection
        is_safe, msg = cls.check_prompt_injection(query)
        if not is_safe:
            return False, msg
        
        return True, "Input sanitized successfully"
