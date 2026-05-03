from fastapi import APIRouter, HTTPException, Header, status
from typing import Optional
from routes.auth_routes import verify_token
from database import db

router = APIRouter(prefix="/manager", tags=["Manager"])


def verify_manager_access(user: dict) -> bool:
    return user and user.get("role") in ["manager", "admin"]


@router.get("/dashboard-stats")
async def get_manager_dashboard_stats(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    token = authorization.split(" ")[1]
    user = verify_token(token)

    if not user or not verify_manager_access(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )

    security_events = db.get_security_events()
    blocked = len([e for e in security_events if e["status"] == "blocked"])
    allowed = len([e for e in security_events if e["status"] == "allowed"])
    suspicious = len([e for e in security_events if "suspicious" in e["event_type"].lower() or e["status"] == "blocked"])

    return {
        "stats": {
            "system_health": max(0, 100 - suspicious * 3),
            "ai_requests": allowed + blocked,
            "requests_allowed": allowed,
            "requests_blocked": blocked,
            "suspicious_activity": suspicious
        }
    }


@router.get("/security-events")
async def get_manager_security_events(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    token = authorization.split(" ")[1]
    user = verify_token(token)

    if not user or not verify_manager_access(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )

    events = db.get_security_events()
    filtered = [
        e for e in events
        if "suspicious" in e["event_type"].lower() or e["status"] == "blocked" or e["user"] == user["username"]
    ]

    return {
        "security_events": filtered,
        "total_events": len(filtered)
    }
