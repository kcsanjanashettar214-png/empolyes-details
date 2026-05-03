# Layer 4: Threat Detection - Classify requests as safe or malicious
from typing import Tuple, Dict
import re
from services.ml_model import threat_model

class ThreatDetector:
    """Layer 4: Threat Detection - Classify and score threat level"""
    
    THREAT_KEYWORDS = {
        "high": ["delete", "drop", "destroy", "wipe", "breach", "hack", "exploit"],
        "medium": ["bypass", "ignore", "override", "disable", "admin", "root", "sudo"],
        "low": ["show", "reveal", "display", "print"]
    }
    
    SUSPICIOUS_PATTERNS = [
        (r"all.*password", "high"),
        (r"all.*salary", "high"),
        (r"all.*employee.*data", "high"),
        (r"system.*command", "high"),
        (r"execute.*code", "high"),
        (r"bypass.*security", "high"),
        (r"admin.*access", "medium"),
        (r"unauthorized.*access", "high"),
    ]
    
    @classmethod
    def detect_threat(cls, query: str) -> Dict:
        """Analyze query for threats"""
        threat_score = 0
        detected_threats = []
        severity = "safe"
        
        # Check threat keywords
        query_lower = query.lower()
        for level, keywords in cls.THREAT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    score = {"high": 0.8, "medium": 0.5, "low": 0.2}.get(level, 0.1)
                    threat_score = max(threat_score, score)
                    detected_threats.append(f"{keyword} ({level})")
        
        # Check patterns
        for pattern, level in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, query_lower):
                score = {"high": 0.9, "medium": 0.6, "low": 0.3}.get(level, 0.1)
                threat_score = max(threat_score, score)
                severity = level
        
        # Apply trained model for network-style threats if text includes a URL or suspicious indicator
        ml_result = threat_model.predict_from_text(query)
        if ml_result['classification'] == 'MALICIOUS':
            threat_score = max(threat_score, ml_result['score'])
            classification = 'MALICIOUS'
            severity = 'high'
            detected_threats.append('ml_model_prediction')

        # Determine final classification
        if threat_score >= 0.7:
            classification = "MALICIOUS"
            severity = "high"
        elif threat_score >= 0.4:
            classification = "SUSPICIOUS"
            severity = "medium"
        else:
            classification = "SAFE"
            severity = "low"
        
        return {
            "classification": classification,
            "threat_score": round(threat_score, 2),
            "severity": severity,
            "detected_threats": detected_threats,
            "ml_model_result": ml_result,
            "is_safe": classification == "SAFE"
        }
