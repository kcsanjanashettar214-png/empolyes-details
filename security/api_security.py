# Layer 2: API Security - Validate request format and rate limiting
from datetime import datetime, timedelta
from typing import Dict, Tuple
import json

class APISecurityValidator:
    """Layer 2: API Security - Request validation and rate limiting"""
    
    def __init__(self, max_requests_per_minute: int = 10):
        self.max_requests_per_minute = max_requests_per_minute
        self.request_history = {}
    
    def validate_request_format(self, request_data: Dict) -> Tuple[bool, str]:
        """Validate request has required fields"""
        required_fields = ["query", "user"]
        
        for field in required_fields:
            if field not in request_data:
                return False, f"Missing required field: {field}"
        
        if not isinstance(request_data.get("query"), str):
            return False, "Query must be a string"
        
        if len(request_data.get("query", "")) == 0:
            return False, "Query cannot be empty"
        
        if len(request_data.get("query", "")) > 5000:
            return False, "Query exceeds maximum length (5000 chars)"
        
        return True, "Request format valid"
    
    def check_rate_limit(self, user_id: str) -> Tuple[bool, str]:
        """Check if user exceeds rate limit"""
        now = datetime.now()
        
        if user_id not in self.request_history:
            self.request_history[user_id] = []
        
        # Clean old requests (older than 1 minute)
        cutoff_time = now - timedelta(minutes=1)
        self.request_history[user_id] = [
            req_time for req_time in self.request_history[user_id]
            if req_time > cutoff_time
        ]
        
        # Check if rate limit exceeded
        if len(self.request_history[user_id]) >= self.max_requests_per_minute:
            return False, f"Rate limit exceeded: {self.max_requests_per_minute} requests per minute"
        
        # Add current request
        self.request_history[user_id].append(now)
        return True, "Rate limit OK"
