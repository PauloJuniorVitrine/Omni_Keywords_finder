# API Key Management
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional, List
import secrets
import hashlib
import time

security = HTTPBearer()

class APIKeyManager:
    def __init__(self):
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        self.key_prefix = "omni_"
    
    def generate_api_key(self, user_id: str, permissions: List[str] = None) -> str:
        """Generate a new API key"""
        # Generate random key
        random_bytes = secrets.token_bytes(32)
        api_key = self.key_prefix + secrets.token_urlsafe(32)
        
        # Hash the key for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Store key info
        self.api_keys[key_hash] = {
            "user_id": user_id,
            "permissions": permissions or [],
            "created_at": time.time(),
            "last_used": None,
            "is_active": True
        }
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return user info"""
        if not api_key.startswith(self.key_prefix):
            return None
        
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        key_info = self.api_keys.get(key_hash)
        
        if not key_info or not key_info["is_active"]:
            return None
        
        # Update last used
        key_info["last_used"] = time.time()
        return key_info
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke an API key"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        if key_hash in self.api_keys:
            self.api_keys[key_hash]["is_active"] = False
            return True
        return False
    
    def get_user_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all API keys for a user"""
        user_keys = []
        for key_hash, key_info in self.api_keys.items():
            if key_info["user_id"] == user_id:
                user_keys.append({
                    "key_hash": key_hash,
                    "permissions": key_info["permissions"],
                    "created_at": key_info["created_at"],
                    "last_used": key_info["last_used"],
                    "is_active": key_info["is_active"]
                })
        return user_keys

api_key_manager = APIKeyManager()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Get current user from API key"""
    api_key = credentials.credentials
    user_info = api_key_manager.validate_api_key(api_key)
    
    if not user_info:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_info

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Check permission logic here
            return await func(*args, **kwargs)
        return wrapper
    return decorator 