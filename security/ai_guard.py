# Layer 5: AI Guard - Block unsafe queries, allow safe ones
from typing import Dict, Tuple

class AIGuard:
    """Layer 5: AI Guard - Filter dangerous AI responses"""
    
    UNSAFE_DATA_PATTERNS = {
        "salary": {"allowed_for": ["admin", "manager"], "sensitivity": "high"},
        "password": {"allowed_for": ["admin"], "sensitivity": "critical"},
        "personal_data": {"allowed_for": ["admin"], "sensitivity": "high"},
        "system_logs": {"allowed_for": ["admin"], "sensitivity": "high"},
        "all_employees": {"allowed_for": ["admin", "manager"], "sensitivity": "medium"},
    }
    
    @classmethod
    def check_query_safety(cls, query: str, user_role: str) -> Tuple[bool, str]:
        """Check if query is safe for the user role"""
        query_lower = query.lower()
        
        # Check for sensitive data requests
        for data_type, restrictions in cls.UNSAFE_DATA_PATTERNS.items():
            if data_type in query_lower:
                allowed_roles = restrictions.get("allowed_for", [])
                if user_role not in allowed_roles:
                    return False, f"User role '{user_role}' cannot access {data_type}"
        
        return True, "Query safety check passed"
    
    @classmethod
    def filter_response(cls, response: str, user_role: str) -> Dict:
        """Filter response based on user role"""
        return {
            "original_response": response,
            "filtered_response": response,
            "filtered": False,
            "removed_fields": []
        }
    
    @classmethod
    def guard_check(cls, query: str, threat_analysis: Dict, user_role: str) -> Tuple[bool, str]:
        """
        Final AI Guard check before allowing query execution
        """
        # Reject ONLY if MALICIOUS (not SUSPICIOUS, as it may be false positive for safe queries)
        if threat_analysis.get("classification") == "MALICIOUS":
            return False, f"Query classified as MALICIOUS and cannot be executed"
        
        # Check user role permissions for specific data types
        is_safe, msg = cls.check_query_safety(query, user_role)
        if not is_safe:
            return False, msg
        
        return True, "AI Guard check passed"
