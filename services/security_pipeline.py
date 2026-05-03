# Security Pipeline - Orchestrates all 7 security layers
from typing import Dict, Tuple
from security.access_control import AccessControl
from security.api_security import APISecurityValidator
from security.input_sanitization import InputSanitizer
from security.threat_detection import ThreatDetector
from security.ai_guard import AIGuard
from security.encryption import encryption_manager
from security.blockchain_logger import blockchain
from services.ml_model import threat_model
from database import db
import json

class SecurityPipeline:
    """
    7-Layer Security Pipeline for request processing
    """
    
    def __init__(self):
        self.api_security = APISecurityValidator()
    
    def process_request(self, request_data: Dict, user: Dict) -> Dict:
        """
        Process request through all 7 security layers
        Returns security report with decision
        """
        
        query = request_data.get("query", "")
        username = user.get("username", "unknown")
        user_role = user.get("role", "unknown")
        prompt_analysis = threat_model.analyze_prompt(query, user_role)
        
        # Initialize security report
        security_report = {
            "query": query,
            "user": username,
            "role": user_role,
            "passed": True,
            "layers": {},
            "blocked_at_layer": None,
            "threat_detected": False,
            "encrypted_response": None,
            "blockchain_log": None,
            "prompt_analysis": prompt_analysis
        }
        
        # Layer 1: Access Control
        is_allowed, access_msg = AccessControl.verify_user_access(user, "query_own_department")
        security_report["layers"]["1_access_control"] = {
            "passed": is_allowed,
            "message": access_msg
        }
        if not is_allowed:
            security_report["passed"] = False
            security_report["blocked_at_layer"] = 1
            self._log_blocked_request(security_report)
            return security_report
        
        # Layer 2: API Security
        is_valid, format_msg = self.api_security.validate_request_format(request_data)
        security_report["layers"]["2_api_security"] = {
            "passed": is_valid,
            "message": format_msg
        }
        if not is_valid:
            security_report["passed"] = False
            security_report["blocked_at_layer"] = 2
            self._log_blocked_request(security_report)
            return security_report
        
        rate_ok, rate_msg = self.api_security.check_rate_limit(username)
        security_report["layers"]["2_rate_limiting"] = {
            "passed": rate_ok,
            "message": rate_msg
        }
        if not rate_ok:
            security_report["passed"] = False
            security_report["blocked_at_layer"] = 2
            self._log_blocked_request(security_report)
            return security_report
        
        # Layer 3: Input Sanitization
        is_sanitized, sanitize_msg = InputSanitizer.sanitize(query)
        security_report["layers"]["3_input_sanitization"] = {
            "passed": is_sanitized,
            "message": sanitize_msg
        }
        if not is_sanitized:
            security_report["passed"] = False
            security_report["blocked_at_layer"] = 3
            security_report["threat_detected"] = True
            self._log_blocked_request(security_report)
            return security_report
        
        # Layer 4: Threat Detection
        threat_analysis = ThreatDetector.detect_threat(query)
        security_report["layers"]["4_threat_detection"] = {
            "passed": threat_analysis["is_safe"],
            "threat_score": threat_analysis["threat_score"],
            "classification": threat_analysis["classification"],
            "severity": threat_analysis["severity"],
            "detected_threats": threat_analysis["detected_threats"]
        }
        # Only block if MALICIOUS, not SUSPICIOUS (which might be false positive)
        if threat_analysis["classification"] == "MALICIOUS":
            security_report["passed"] = False
            security_report["blocked_at_layer"] = 4
            security_report["threat_detected"] = True
            self._log_blocked_request(security_report)
            return security_report
        
        # Layer 5: AI Guard
        is_safe, guard_msg = AIGuard.guard_check(query, threat_analysis, user_role)
        security_report["layers"]["5_ai_guard"] = {
            "passed": is_safe,
            "message": guard_msg
        }
        if not is_safe:
            security_report["passed"] = False
            security_report["blocked_at_layer"] = 5
            security_report["threat_detected"] = True
            self._log_blocked_request(security_report)
            return security_report
        
        # Layer 6: Encryption (for response)
        security_report["layers"]["6_encryption"] = {
            "passed": True,
            "message": "Encryption enabled for response"
        }
        
        # Layer 7: Blockchain Logging
        blockchain_entry = blockchain.add_log({
            "type": "request_allowed",
            "user": username,
            "role": user_role,
            "query": query[:100],  # First 100 chars
            "timestamp": security_report["layers"]["1_access_control"]["message"]
        })
        security_report["layers"]["7_blockchain_logging"] = {
            "passed": True,
            "message": f"Logged in blockchain - Block #{blockchain_entry['index']}",
            "block_id": blockchain_entry["index"]
        }
        
        # Log allowed prompt submission with metadata
        prompt_data = {
            "event_type": "prompt_submission",
            "user": username,
            "role": user_role,
            "status": "allowed",
            "details": f"Prompt allowed with trust {prompt_analysis['trust_score']}%.",
            "query": query,
            "src_ip": prompt_analysis["src_ip"],
            "location": prompt_analysis["location"],
            "trust_score": prompt_analysis["trust_score"],
            "real_or_dummy": prompt_analysis["real_or_dummy"],
            "classification": prompt_analysis["classification"],
            "meta": prompt_analysis
        }
        db.add_security_event(prompt_data)
        db.add_prompt_event(prompt_data)
        
        return security_report
    
    def _log_blocked_request(self, security_report: Dict):
        """Log blocked request to database and blockchain"""
        prompt_analysis = security_report.get("prompt_analysis", {})

        # Add threat log
        if security_report.get("threat_detected"):
            db.add_threat_log({
                "type": "security_violation",
                "severity": "high" if security_report.get("blocked_at_layer") <= 3 else "medium",
                "message": security_report["layers"].get(
                    f"{security_report['blocked_at_layer']}_" + 
                    list(security_report["layers"].keys())[security_report["blocked_at_layer"]-1].split("_", 1)[1],
                    "Request blocked"
                ),
                "user": security_report["user"],
                "query": security_report["query"][:100],
                "blocked": True
            })
        
        # Add to blockchain
        blockchain.add_log({
            "type": "request_blocked",
            "user": security_report["user"],
            "role": security_report["role"],
            "blocked_at_layer": security_report["blocked_at_layer"],
            "query": security_report["query"][:100],
            "threat": security_report.get("threat_detected", False)
        })
        
        # Add security event for blocked request
        db.add_security_event({
            "event_type": "request_blocked",
            "user": security_report["user"],
            "status": "blocked",
            "details": f"Blocked at Layer {security_report['blocked_at_layer']}",
            "meta": prompt_analysis
        })
        
        # Add prompt audit event for blocked prompt
        db.add_prompt_event({
            "event_type": "prompt_submission",
            "user": security_report["user"],
            "role": security_report["role"],
            "status": "blocked",
            "details": f"Blocked prompt at layer {security_report['blocked_at_layer']}.",
            "query": security_report["query"],
            "src_ip": prompt_analysis.get("src_ip", "unknown"),
            "location": prompt_analysis.get("location", "unknown"),
            "trust_score": prompt_analysis.get("trust_score", 0),
            "real_or_dummy": prompt_analysis.get("real_or_dummy", "unknown"),
            "classification": prompt_analysis.get("classification", "unknown"),
            "meta": prompt_analysis
        })
