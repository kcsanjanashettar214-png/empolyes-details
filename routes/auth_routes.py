# Authentication routes
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
import config
from database import db

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login endpoint with mock user database
    Test credentials:
    - username: employee, password: employee123
    - username: manager, password: manager123
    - username: admin, password: admin123
    """
    
    # Validate user
    user = config.USERS.get(request.username)
    if not user or user["password"] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create JWT token
    access_token = create_access_token(request.username, user["role"])
    
    db.add_security_event({
        "event_type": "user_login",
        "user": request.username,
        "status": "success",
        "details": f"User logged in with role {user['role']}",
        "meta": {
            "role": user["role"],
            "department": user["department"],
            "timestamp": datetime.utcnow().isoformat()
        }
    })

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "username": request.username,
            "role": user["role"],
            "department": user["department"]
        }
    )

def create_access_token(username: str, role: str):
    """Create JWT access token"""
    expires = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": username,
        "role": role,
        "exp": expires
    }
    token = jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return token

def verify_token(token: str):
    """Verify JWT token and extract user info"""
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if username is None:
            return None
        return {
            "username": username,
            "role": role,
            "department": config.USERS.get(username, {}).get("department", "")
        }
    except JWTError:
        return None
