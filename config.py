# Configuration
import os
from datetime import timedelta

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database Configuration
DATABASE_URL = "sqlite:///./test.db"

# Security Configuration
ENCRYPTION_KEY = "your-encryption-key-32-chars-long"
MAX_REQUESTS_PER_MINUTE = 10

# Malicious Keywords for Detection
MALICIOUS_KEYWORDS = [
    "ignore", "bypass", "reveal", "admin", "password",
    "delete", "drop", "exec", "execute", "shell",
    "override", "disable", "hack", "inject", "sql",
    "system", "sudo", "root", "secret", "token"
]

# Mock User Database
USERS = {
    "employee": {
        "password": "employee123",
        "role": "employee",
        "department": "Operations"
    },
    "manager": {
        "password": "manager123",
        "role": "manager",
        "department": "Sales"
    },
    "admin": {
        "password": "admin123",
        "role": "admin",
        "department": "IT"
    }
}

# Role Permissions
ROLE_PERMISSIONS = {
    "employee": ["view_own_data", "query_own_department"],
    "manager": ["view_own_data", "query_own_department", "view_team_analytics"],
    "admin": ["view_all_data", "query_all_departments", "view_system_logs", "manage_users"]
}

# Sample Company Data
COMPANY_DATA = {
    "employees": [
        {"id": 1, "name": "John Doe", "role": "Engineer", "department": "Operations", "salary": 75000, "attendance": "95%"},
        {"id": 2, "name": "Jane Smith", "role": "Manager", "department": "Sales", "salary": 85000, "attendance": "98%"},
        {"id": 3, "name": "Bob Johnson", "role": "Analyst", "department": "Operations", "salary": 65000, "attendance": "92%"},
    ],
    "departments": {
        "Operations": {"performance": "85%", "budget": 500000, "head_count": 15},
        "Sales": {"performance": "92%", "budget": 400000, "head_count": 10},
        "IT": {"performance": "88%", "budget": 300000, "head_count": 8},
    }
}
