"""
AI-Powered Enterprise Dashboard
7-Layer Security Architecture (Chakravyuh Model)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import routes.auth_routes as auth_routes
import routes.ai_routes as ai_routes
import routes.admin_routes as admin_routes
import routes.manager_routes as manager_routes
import routes.network_routes as network_routes

# Create FastAPI app
app = FastAPI(
    title="Secure Enterprise Dashboard",
    description="AI-powered dashboard with 7-layer security architecture",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(ai_routes.router)
app.include_router(admin_routes.router)
app.include_router(manager_routes.router)
app.include_router(network_routes.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Secure Enterprise Dashboard",
        "version": "1.0.0",
        "security_layers": 7,
        "description": "AI-powered enterprise dashboard with Chakravyuh security model"
    }

@app.get("/info")
async def info():
    """API information endpoint"""
    return {
        "api_name": "Secure Enterprise Dashboard API",
        "endpoints": {
            "authentication": "/auth/login",
            "queries": "/api/query",
            "health": "/api/health",
            "admin": "/admin/*"
        },
        "security_layers": [
            "1. Access Control",
            "2. API Security (Rate Limiting, Format Validation)",
            "3. Input Sanitization (Keyword Detection)",
            "4. Threat Detection",
            "5. AI Guard",
            "6. Encryption",
            "7. Blockchain Logging"
        ],
        "test_users": [
            {"username": "employee", "password": "employee123", "role": "employee"},
            {"username": "manager", "password": "manager123", "role": "manager"},
            {"username": "admin", "password": "admin123", "role": "admin"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
