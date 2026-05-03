# AI Query routes with security pipeline
from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel
from typing import Optional
from routes.auth_routes import verify_token
from services.security_pipeline import SecurityPipeline
from services.ai_service import AIService
from security.encryption import encryption_manager
from database import db

router = APIRouter(prefix="/api", tags=["AI Query"])

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    encrypted_response: Optional[str] = None
    security_status: dict = {}
    analysis: dict = {}
    message: str

pipeline = SecurityPipeline()

@router.post("/query", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Process a query through the 7-layer security pipeline
    """
    
    # Extract token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split(" ")[1]
    user = verify_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Run through security pipeline
    request_data = {"query": request.query, "user": user}
    security_report = pipeline.process_request(request_data, user)
    
    # If blocked, return error
    if not security_report["passed"]:
        blocked_layer = security_report["blocked_at_layer"]
        layer_name = list(security_report["layers"].keys())[blocked_layer - 1]
        error_msg = security_report["layers"][layer_name]["message"]
        
        return QueryResponse(
            success=False,
            response=None,
            message=f"Request blocked at Layer {blocked_layer}: {error_msg}",
            security_status=security_report,
            analysis=security_report.get("prompt_analysis", {})
        )
    
    # All security layers passed - process query
    ai_response = AIService.process_query(
        request.query,
        user["role"],
        user.get("department", "")
    )
    
    # Encrypt response
    encrypted = encryption_manager.encrypt(ai_response["response"])
    
    return QueryResponse(
        success=True,
        response=ai_response["response"],
        encrypted_response=encrypted,
        message="Query processed successfully",
        security_status=security_report,
        analysis=security_report.get("prompt_analysis", {})
    )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Query API",
        "timestamp": str(__import__('datetime').datetime.now())
    }
