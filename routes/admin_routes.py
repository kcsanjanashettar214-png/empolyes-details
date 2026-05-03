# Admin routes for viewing logs and security data
from fastapi import APIRouter, HTTPException, Header, status
from typing import Optional
from routes.auth_routes import verify_token
from database import db
from security.blockchain_logger import blockchain

router = APIRouter(prefix="/admin", tags=["Admin"])

def verify_admin_access(user: dict) -> bool:
    """Verify user has admin role"""
    return user and user.get("role") == "admin"

@router.get("/blockchain-logs")
async def get_blockchain_logs(authorization: Optional[str] = Header(None)):
    """Get blockchain logs (admin only)"""
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    token = authorization.split(" ")[1]
    user = verify_token(token)
    
    if not user or not verify_admin_access(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return {
        "blockchain_logs": blockchain.get_chain(),
        "integrity_verified": blockchain.verify_integrity(),
        "total_blocks": len(blockchain.get_chain())
    }

@router.get("/threat-logs")
async def get_threat_logs(authorization: Optional[str] = Header(None)):
    """Get threat detection logs (admin only)"""
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    token = authorization.split(" ")[1]
    user = verify_token(token)
    
    if not user or not verify_admin_access(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return {
        "threat_logs": db.get_threat_logs(),
        "total_threats": len(db.threat_logs),
        "critical_threats": len([t for t in db.threat_logs if t["severity"] == "high"])
    }

@router.get("/security-events")
async def get_security_events(authorization: Optional[str] = Header(None)):
    """Get security events (admin only)"""
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    token = authorization.split(" ")[1]
    user = verify_token(token)
    
    if not user or not verify_admin_access(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return {
        "security_events": db.get_security_events(),
        "total_events": len(db.security_events)
    }

@router.get("/prompt-events")
async def get_prompt_events(authorization: Optional[str] = Header(None)):
    """Get recent prompt audit events (admin only)"""
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    token = authorization.split(" ")[1]
    user = verify_token(token)
    
    if not user or not verify_admin_access(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return {
        "prompt_events": db.get_prompt_events(),
        "total_prompt_events": len(db.prompt_events)
    }

@router.get("/dashboard-stats")
async def get_dashboard_stats(authorization: Optional[str] = Header(None)):
    """Get security dashboard statistics"""
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    token = authorization.split(" ")[1]
    user = verify_token(token)
    
    if not user or not verify_admin_access(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    threat_logs = db.get_threat_logs()
    security_events = db.get_security_events()
    prompt_events = db.get_prompt_events()
    login_events = [e for e in security_events if e["event_type"] == "user_login"]
    real_queries = len([e for e in prompt_events if e.get("real_or_dummy") == "REAL"])
    dummy_queries = len([e for e in prompt_events if e.get("real_or_dummy") == "DUMMY"])
    avg_trust_score = round(
        sum(e.get("trust_score", 0) for e in prompt_events) / max(1, len(prompt_events)),
        1
    )
    
    return {
        "stats": {
            "total_threats_detected": len(threat_logs),
            "high_severity_threats": len([t for t in threat_logs if t["severity"] == "high"]),
            "total_security_events": len(security_events),
            "blockchain_blocks": len(blockchain.get_chain()),
            "blockchain_integrity": blockchain.verify_integrity(),
            "requests_blocked": len([e for e in security_events if e["status"] == "blocked"]),
            "requests_allowed": len([e for e in security_events if e["status"] == "allowed"]),
            "prompt_requests": len(prompt_events),
            "real_queries": real_queries,
            "dummy_queries": dummy_queries,
            "avg_trust_score": avg_trust_score,
            "login_events": len(login_events)
        }
    }
