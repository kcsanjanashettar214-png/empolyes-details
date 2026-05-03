# In-memory database for demo purposes
import json
from datetime import datetime
from typing import Dict, List, Optional

class InMemoryDB:
    """Simple in-memory database for demo"""
    
    def __init__(self):
        self.blockchain_logs = []
        self.threat_logs = []
        self.security_events = []
        self.prompt_events = []
        
    def add_blockchain_log(self, data: Dict):
        """Add a log to blockchain"""
        log_entry = {
            "id": len(self.blockchain_logs) + 1,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "previous_hash": self.blockchain_logs[-1].get("hash") if self.blockchain_logs else "genesis",
            "hash": ""
        }
        # Simple hash
        log_entry["hash"] = hash(str(log_entry["data"]) + log_entry["previous_hash"])
        self.blockchain_logs.append(log_entry)
        return log_entry
    
    def add_threat_log(self, threat_data: Dict):
        """Log a threat detection"""
        threat = {
            "id": len(self.threat_logs) + 1,
            "timestamp": datetime.now().isoformat(),
            "severity": threat_data.get("severity", "medium"),
            "type": threat_data.get("type", "unknown"),
            "message": threat_data.get("message", ""),
            "user": threat_data.get("user", "unknown"),
            "query": threat_data.get("query", ""),
            "blocked": threat_data.get("blocked", True)
        }
        self.threat_logs.append(threat)
        return threat
    
    def add_security_event(self, event: Dict):
        """Log a security event"""
        security_event = {
            "id": len(self.security_events) + 1,
            "timestamp": datetime.now().isoformat(),
            "event_type": event.get("event_type", ""),
            "user": event.get("user", ""),
            "status": event.get("status", ""),
            "details": event.get("details", ""),
            "meta": event.get("meta", {})
        }
        self.security_events.append(security_event)
        return security_event
    
    def add_prompt_event(self, prompt_data: Dict):
        """Add a prompt audit event"""
        prompt_event = {
            "id": len(self.prompt_events) + 1,
            "timestamp": datetime.now().isoformat(),
            "event_type": prompt_data.get("event_type", "prompt_submission"),
            "user": prompt_data.get("user", "unknown"),
            "role": prompt_data.get("role", "unknown"),
            "status": prompt_data.get("status", "unknown"),
            "src_ip": prompt_data.get("src_ip", "unknown"),
            "location": prompt_data.get("location", "unknown"),
            "trust_score": prompt_data.get("trust_score", 0),
            "real_or_dummy": prompt_data.get("real_or_dummy", "unknown"),
            "classification": prompt_data.get("classification", "unknown"),
            "query": prompt_data.get("query", "")[:150],
            "details": prompt_data.get("details", ""),
            "meta": prompt_data.get("meta", {})
        }
        self.prompt_events.append(prompt_event)
        return prompt_event
    
    def get_blockchain_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent blockchain logs"""
        return self.blockchain_logs[-limit:]

    def get_prompt_events(self, limit: int = 50) -> List[Dict]:
        """Get recent prompt audit events"""
        return self.prompt_events[-limit:]
    
    def get_threat_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent threat logs"""
        return self.threat_logs[-limit:]
    
    def get_security_events(self, limit: int = 50) -> List[Dict]:
        """Get recent security events"""
        return self.security_events[-limit:]

# Global database instance
db = InMemoryDB()
