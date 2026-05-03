# Layer 1: Access Control - Verify user role and permissions
from typing import Dict, Optional
from config import ROLE_PERMISSIONS

class AccessControl:
    """Layer 1: Access Control - Validate user authentication and authorization"""
    
    @staticmethod
    def verify_user_access(user: Dict, required_permission: str) -> tuple[bool, str]:
        """
        Verify if user has required permission
        Returns: (is_allowed, message)
        """
        if not user:
            return False, "No user authenticated"
        
        user_role = user.get("role", "")
        user_permissions = ROLE_PERMISSIONS.get(user_role, [])
        
        if required_permission not in user_permissions:
            return False, f"User role '{user_role}' does not have permission: {required_permission}"
        
        return True, "Access granted"
    
    @staticmethod
    def check_role_access(user: Dict) -> Dict:
        """Get role-based access information"""
        if not user:
            return {"authenticated": False, "role": None, "permissions": []}
        
        role = user.get("role", "")
        permissions = ROLE_PERMISSIONS.get(role, [])
        
        return {
            "authenticated": True,
            "role": role,
            "permissions": permissions,
            "username": user.get("username", "")
        }
